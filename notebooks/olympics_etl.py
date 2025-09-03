# Databricks notebook source
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, DoubleType, BooleanType, DateType

# COMMAND ----------

# --- 0) Fill these with your real values (use a NEW regenerated secret!) ---
TENANT_ID   = ""
APP_ID      = ""

# Strongly recommend storing the secret in a Databricks secret scope
# Example: APP_SECRET = dbutils.secrets.get("kv-scope", "sp-secret")
APP_SECRET  = ""

STORAGE_ACCT = "tokyoolympicdatajovan"
CONTAINER    = "tokyo-olumpic-data"  
MOUNT_POINT  = "/mnt/tokyo-olympic"

# --- 1) OAuth configs (v2 endpoint) ---
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": APP_ID,
  "fs.azure.account.oauth2.client.secret": APP_SECRET,
  "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
}

# --- 2) Clean old mount (ignore errors if not mounted) ---
try:
    if any(m.mountPoint == MOUNT_POINT for m in dbutils.fs.mounts()):
        dbutils.fs.unmount(MOUNT_POINT)
except Exception as e:
    print(f"[warn] unmount skipped: {e}")

# --- 3) Mount the container ---
dbutils.fs.mount(
    source=f"abfss://{CONTAINER}@{STORAGE_ACCT}.dfs.core.windows.net/",
    mount_point=MOUNT_POINT,
    extra_configs=configs
)

print("[ok] Mounted:", MOUNT_POINT)

# --- 4) Smoke test: list, write a tiny file, read it back ---
display(dbutils.fs.ls(MOUNT_POINT))

test_path = f"{MOUNT_POINT}/_healthcheck.txt"
dbutils.fs.put(test_path, "hello from databricks\n", overwrite=True)
print("[ok] wrote:", test_path)

print(dbutils.fs.head(test_path))


# COMMAND ----------

# ================================================================
# ONE-PASS PIPELINE: raw CSV -> cleaned Delta (transformed-data)
# Container mounted at /mnt/tokyo-olympic
# ================================================================

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
from pyspark.sql import functions as F, Window as W

# --- Small-data tuning
spark.conf.set("spark.sql.shuffle.partitions", "8")
spark.conf.set("spark.sql.adaptive.enabled", "true")

# --- Paths
MOUNT_POINT = "/mnt/tokyo-olympic"
RAW_PATH    = f"{MOUNT_POINT}/raw-data"
OUT_BASE    = f"{MOUNT_POINT}/transformed-data"   # final, cleaned Delta outputs

# --- Filenames (ensure case matches blobs)
files = {
    "athletes":      "athletes.csv",
    "coaches":       "coaches.csv",
    "entriesgender": "entriesgender.csv",
    "medals":        "medals.csv",
    "teams":         "teams.csv",
}

# --- Explicit schemas
athletes_schema = StructType([
    StructField("PersonName", StringType(), True),
    StructField("Country",     StringType(), True),
    StructField("Discipline",  StringType(), True),
])
coaches_schema = StructType([
    StructField("Name",       StringType(), True),
    StructField("Country",    StringType(), True),
    StructField("Discipline", StringType(), True),
    StructField("Event",      StringType(), True),
])
entriesgender_schema = StructType([
    StructField("Discipline", StringType(), True),
    StructField("Female",     IntegerType(), True),
    StructField("Male",       IntegerType(), True),
    StructField("Total",      IntegerType(), True),
])
medals_schema = StructType([
    StructField("Rank",          IntegerType(), True),
    StructField("TeamCountry",   StringType(),  True),
    StructField("Gold",          IntegerType(), True),
    StructField("Silver",        IntegerType(), True),
    StructField("Bronze",        IntegerType(), True),
    StructField("Total",         IntegerType(), True),
    StructField("Rank by Total", IntegerType(), True),  # will be renamed later
])
teams_schema = StructType([
    StructField("TeamName",   StringType(), True),
    StructField("Discipline", StringType(), True),
    StructField("Country",    StringType(), True),
    StructField("Event",      StringType(), True),
])

schemas = {
    "athletes":      athletes_schema,
    "coaches":       coaches_schema,
    "entriesgender": entriesgender_schema,
    "medals":        medals_schema,
    "teams":         teams_schema,
}

# --- Helpers (trim, standardize, IDs, safe ops)
def trim_all_strings(df):
    exprs = []
    for c, t in df.dtypes:
        if t == "string":
            exprs.append(F.regexp_replace(F.trim(F.col(c)), r"\s+", " ").alias(c))
        else:
            exprs.append(F.col(c))
    return df.select(*exprs)

def initcap_cols(df, cols):
    for c in cols:
        if c in df.columns:
            df = df.withColumn(c, F.initcap(F.col(c)))
    return df

def add_meta(df):
    return (df
            .withColumn("ingestion_date", F.current_date())
            .withColumn("source_file", F.input_file_name()))

def hash_id(df, id_col, cols):
    return df.withColumn(
        id_col,
        F.sha2(
            F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("")) for c in cols]),
            256
        )
    )

def clean_int_col(df, col):
    # safety net: remove commas/spaces etc. and cast to int
    return df.withColumn(col, F.regexp_replace(F.col(col).cast("string"), r"[^0-9\-]", "").cast("int"))

def safe_div(num, den):
    """Safe division for Spark Columns (num, den are already Column objects)."""
    return F.when((den.isNull()) | (den == 0), F.lit(None).cast(DoubleType())) \
            .otherwise(num.cast(DoubleType()) / den.cast(DoubleType()))

# --- FS utilities to ensure Delta-ready targets
def path_exists(path: str) -> bool:
    try:
        dbutils.fs.ls(path)
        return True
    except Exception:
        return False

def has_delta_log(path: str) -> bool:
    try:
        entries = dbutils.fs.ls(path)
        names = [e.name for e in entries]
        return any(n == "_delta_log/" or n.endswith("_delta_log") for n in names)
    except Exception:
        return False

def prep_delta_target(path: str, clean_non_delta: bool = True):
    """
    Ensures the directory is suitable for a Delta write:
    - If path doesn't exist: do nothing.
    - If path exists and has _delta_log: do nothing.
    - If path exists and is non-Delta:
        - If clean_non_delta: delete it.
        - Else: try convert in place from Parquet to Delta.
    """
    if not path_exists(path):
        return
    if has_delta_log(path):
        return
    if clean_non_delta:
        print(f"[CLEAN] Removing existing non-Delta folder: {path}")
        dbutils.fs.rm(path, recurse=True)
    else:
        print(f"[CONVERT] Converting existing Parquet folder to Delta: {path}")
        from delta.tables import DeltaTable
        DeltaTable.convertToDelta(spark, f"parquet.`{path}`")

# --- Load raw CSVs with explicit schemas
dfs = {}
for name, fname in files.items():
    path = f"{RAW_PATH}/{fname}"
    print("="*78)
    print(f"[LOAD] {name}  ←  {path}")

    df = (spark.read
                .option("header", True)
                .schema(schemas[name])
                .csv(path))

    # Only entriesgender has numeric counts; sanitize if needed
    if name == "entriesgender":
        for c in ["Female", "Male", "Total"]:
            df = clean_int_col(df, c)

    print("[DQ] Null counts:")
    display(df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]))
    display(df.limit(5))

    dfs[name] = df

# --- Transform (Silver logic) and write Delta
for name, df in dfs.items():
    print("="*78)
    print(f"[TRANSFORM] {name}")

    if name == "athletes":
        x = df.transform(trim_all_strings)
        x = (x
             .withColumn("FirstName", F.regexp_extract(F.col("PersonName"), r"^(.*)\s+(\S+)$", 1))
             .withColumn("LastName",  F.regexp_extract(F.col("PersonName"), r"^(.*)\s+(\S+)$", 2))
             .withColumn("FirstName", F.when(F.col("FirstName") == "", F.col("PersonName")).otherwise(F.col("FirstName")))
             .withColumn("LastName",  F.when(F.col("FirstName") == F.col("PersonName"), F.lit(None)).otherwise(F.col("LastName"))))
        x = initcap_cols(x, ["Discipline"])
        x = hash_id(x, "athlete_id", ["PersonName", "Country", "Discipline"])
        x = add_meta(x).dropDuplicates()

    elif name == "coaches":
        x = df.transform(trim_all_strings)
        x = initcap_cols(x, ["Discipline", "Event"])
        x = hash_id(x, "coach_id", ["Name", "Country", "Discipline", "Event"])
        x = add_meta(x).dropDuplicates()

    elif name == "entriesgender":
        x = df.transform(trim_all_strings)
        x = initcap_cols(x, ["Discipline"])
        x = (x
             .withColumn("Female", F.col("Female").cast("int"))
             .withColumn("Male",   F.col("Male").cast("int"))
             .withColumn("Total_calc", (F.col("Female") + F.col("Male")).cast("int"))
             .withColumn("Total", F.when(F.col("Total").isNull(), F.col("Total_calc")).otherwise(F.col("Total")))
             .withColumn("total_matches", F.col("Total") == F.col("Total_calc"))
             .withColumn("female_share", safe_div(F.col("Female"), F.col("Total")))
             .withColumn("male_share",   safe_div(F.col("Male"),   F.col("Total")))
             .drop("Total_calc"))
        x = add_meta(x).dropDuplicates()

        print("[CHECK] Female + Male vs Total")
        display(x.select(
            F.sum("Female").alias("sum_female"),
            F.sum("Male").alias("sum_male"),
            F.sum("Total").alias("sum_total"),
            (F.sum("Female") + F.sum("Male")).alias("sum_f_plus_m")
        ))

    elif name == "medals":
        x = df.transform(trim_all_strings)

        # --- Delta-safe column rename
        if "Rank by Total" in x.columns:
            x = x.withColumnRenamed("Rank by Total", "RankByTotal")

        x = (x
             .withColumn("Gold",   F.col("Gold").cast("int"))
             .withColumn("Silver", F.col("Silver").cast("int"))
             .withColumn("Bronze", F.col("Bronze").cast("int"))
             .withColumn("Total_calc", (F.col("Gold") + F.col("Silver") + F.col("Bronze")).cast("int"))
             .withColumn("Total", F.when(F.col("Total").isNull(), F.col("Total_calc")).otherwise(F.col("Total")))
             .drop("Total_calc"))

        w_gold  = W.orderBy(F.col("Gold").desc(),  F.col("Silver").desc(), F.col("Bronze").desc())
        w_total = W.orderBy(F.col("Total").desc(), F.col("Gold").desc(),   F.col("Silver").desc())
        x = (x
             .withColumn("medal_points", 3*F.col("Gold") + 2*F.col("Silver") + F.col("Bronze"))
             .withColumn("rank_by_gold",  F.dense_rank().over(w_gold))
             .withColumn("rank_by_total", F.dense_rank().over(w_total)))
        x = add_meta(x).dropDuplicates()

    elif name == "teams":
        x = df.transform(trim_all_strings)
        x = initcap_cols(x, ["Discipline", "Event"])
        x = hash_id(x, "team_id", ["TeamName", "Country", "Discipline", "Event"])
        x = add_meta(x).dropDuplicates()

    else:
        x = df  # fallback

    # --- Ensure target is Delta-ready, then write
    out = f"{OUT_BASE}/{name}"
    prep_delta_target(out, clean_non_delta=True)  # deletes non-Delta folders if present

    (x.write.format("delta").mode("overwrite").save(out))
    print(f"[ok] wrote delta -> {out}")

print("="*78)
print("[DONE] All datasets written to /mnt/tokyo-olympic/transformed-data")


# COMMAND ----------

