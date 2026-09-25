-- ============================================================
-- FRAUD DETECTION — Parte 1: Data Analyst
-- Script 01: Analisis de patrones de fraude
-- Dataset: Credit Card Fraud Detection (Kaggle)
-- Motor: DuckDB
-- ============================================================

-- 2. DISTRIBUCION DEL TARGET
SELECT
    Class                                                   AS fraude,
    COUNT(*)                                                AS transacciones,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 4)      AS porcentaje,
    ROUND(AVG(Amount), 2)                                   AS monto_medio,
    ROUND(MEDIAN(Amount), 2)                                AS monto_mediana,
    ROUND(MAX(Amount), 2)                                   AS monto_max
FROM read_csv_auto('data/raw/creditcard.csv')
GROUP BY 1
ORDER BY 1;

-- 3. ANALISIS TEMPORAL — TASA DE FRAUDE POR HORA
SELECT
    FLOOR((Time / 3600) % 24)::INTEGER     AS hora_dia,
    COUNT(*)                               AS total,
    SUM(Class)                             AS fraudes,
    ROUND(100.0 * AVG(Class), 4)           AS tasa_fraude_pct,
    ROUND(AVG(Amount), 2)                  AS monto_medio
FROM read_csv_auto('data/raw/creditcard.csv')
GROUP BY 1
ORDER BY tasa_fraude_pct DESC
LIMIT 10;

-- 4. ANALISIS DE MONTOS POR BANDA
SELECT
    CASE
        WHEN Amount = 0              THEN '0. Sin cargo'
        WHEN Amount < 10             THEN '1. Micro (<10)'
        WHEN Amount < 50             THEN '2. Pequeno (10-50)'
        WHEN Amount < 100            THEN '3. Medio (50-100)'
        WHEN Amount < 500            THEN '4. Grande (100-500)'
        WHEN Amount < 1000           THEN '5. Muy grande (500-1k)'
        ELSE                              '6. Enorme (1k+)'
    END                              AS banda_monto,
    COUNT(*)                         AS total,
    SUM(Class)                       AS fraudes,
    ROUND(100.0 * AVG(Class), 4)     AS tasa_fraude_pct,
    ROUND(AVG(Amount), 2)            AS monto_medio
FROM read_csv_auto('data/raw/creditcard.csv')
GROUP BY 1
ORDER BY 1;

-- 5. PATRONES SOSPECHOSOS — COMPONENTES PCA CRITICOS
SELECT
    Class                           AS fraude,
    COUNT(*)                        AS total,
    ROUND(AVG(V3), 4)               AS v3_medio,
    ROUND(AVG(V14), 4)              AS v14_medio,
    ROUND(AVG(V17), 4)              AS v17_medio,
    ROUND(AVG(V4), 4)               AS v4_medio,
    ROUND(AVG(V11), 4)              AS v11_medio,
    -- Regla heuristica simple
    COUNT(*) FILTER (
        WHERE V14 < -5 OR V4 > 3
    )                               AS alertas_regla_simple,
    ROUND(100.0 * COUNT(*) FILTER (
        WHERE V14 < -5 OR V4 > 3
    ) / COUNT(*), 2)                AS pct_alertas
FROM read_csv_auto('data/raw/creditcard.csv')
GROUP BY 1
ORDER BY 1;