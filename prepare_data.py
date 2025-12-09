import pandas as pd

cpi_file = "dataset_2025-12-09T12_18_49.044984292Z_DEFAULT_INTEGRATION_IMF.STA_CPI_5.0.0.csv"
er_file  = "dataset_2025-12-09T12_39_51.842815897Z_DEFAULT_INTEGRATION_IMF.STA_ER_4.0.1.csv"
ir_file  = "dataset_2025-12-09T12_42_14.330798536Z_DEFAULT_INTEGRATION_IMF.STA_MFS_IR_8.0.1.csv"

df_cpi = pd.read_csv(cpi_file)
df_er  = pd.read_csv(er_file)
df_ir  = pd.read_csv(ir_file)

cpi_row = df_cpi[
    (df_cpi["COICOP_1999"] == "All Items") &
    (df_cpi["TYPE_OF_TRANSFORMATION"] == "Period average, Year-over-year (YOY) percent change") &
    (df_cpi["FREQUENCY"] == "Quarterly")
]

cpi_melt = cpi_row.melt(
    id_vars=["FREQUENCY"],
    value_vars=[col for col in df_cpi.columns if col.startswith("20") and "-Q" in col],
    var_name="Quarter",
    value_name="CPI_YoY"
).dropna()

fx_row = df_er[
    (df_er["SERIES_CODE"] == "EGY.XDC_USD.PA_RT.Q")
]

fx_melt = fx_row.melt(
    id_vars=["FREQUENCY"],
    value_vars=[col for col in df_er.columns if col.startswith("20") and "-Q" in col],
    var_name="Quarter",
    value_name="FX"
).dropna()

ir_row = df_ir[
    (df_ir["INDICATOR"] == "Monetary policy-related, Rate, Percent per annum") &
    (df_ir["FREQUENCY"] == "Quarterly")
]

ir_melt = ir_row.melt(
    id_vars=["FREQUENCY"],
    value_vars=[col for col in df_ir.columns if col.startswith("20") and "-Q" in col],
    var_name="Quarter",
    value_name="Policy_Rate"
).dropna()

merged = cpi_melt[["Quarter", "CPI_YoY"]].merge(
    fx_melt[["Quarter", "FX"]], on="Quarter", how="outer"
).merge(
    ir_melt[["Quarter", "Policy_Rate"]], on="Quarter", how="outer"
)

merged["Quarter"] = pd.Categorical(
    merged["Quarter"],
    categories=sorted(merged["Quarter"].unique(), key=lambda x: (int(x.split("-")[0]), int(x.split("Q")[1]))),
    ordered=True
)
merged = merged.sort_values("Quarter").reset_index(drop=True)

merged["Real_Rate"] = merged["Policy_Rate"] - merged["CPI_YoY"]


output_file = "egypt_macro_quarterly.csv"
merged.to_csv(output_file, index=False)
print(merged.head(10))