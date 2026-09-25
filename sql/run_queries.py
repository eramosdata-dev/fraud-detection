import duckdb

con = duckdb.connect()

print("=== PATRONES SOSPECHOSOS — COMPONENTES PCA ===")
resultado = con.execute("""
    SELECT
        Class                           AS fraude,
        COUNT(*)                        AS total,
        ROUND(AVG(V3), 4)               AS v3_medio,
        ROUND(AVG(V14), 4)              AS v14_medio,
        ROUND(AVG(V17), 4)              AS v17_medio,
        ROUND(AVG(V4), 4)               AS v4_medio,
        ROUND(AVG(V11), 4)              AS v11_medio,
        COUNT(*) FILTER (
            WHERE V14 < -5 OR V4 > 3
        )                               AS alertas_regla_simple,
        ROUND(100.0 * COUNT(*) FILTER (
            WHERE V14 < -5 OR V4 > 3
        ) / COUNT(*), 2)                AS pct_alertas
    FROM read_csv_auto('data/raw/creditcard.csv')
    GROUP BY 1
    ORDER BY 1
""").df()

print(resultado)
