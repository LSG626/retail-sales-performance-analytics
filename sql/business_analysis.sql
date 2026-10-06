-- Executive KPIs
SELECT

    ROUND(SUM(revenue), 2) AS total_revenue,

    COUNT(DISTINCT invoice) AS total_orders,

    COUNT(DISTINCT customer_id) AS total_customers,

    SUM(quantity) AS units_sold,

    ROUND(
        SUM(revenue) /
        COUNT(DISTINCT invoice),
        2
    ) AS average_order_value

FROM retail_transactions

WHERE is_sale = 1;

-- Revenue by Month

SELECT
    year,
    month,
    month_name,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM retail_transactions

WHERE is_sale = 1

GROUP BY
    year,
    month,
    month_name

ORDER BY
    year,
    month;

-- Month-over-Month Growth

WITH monthly_sales AS (

    SELECT
        year,
        month,

        SUM(revenue) AS revenue

    FROM retail_transactions

    WHERE is_sale = 1

    GROUP BY
        year,
        month
),

revenue_growth AS (

    SELECT
        year,
        month,
        revenue,

        LAG(revenue) OVER (
            ORDER BY year, month
        ) AS previous_month_revenue

    FROM monthly_sales
)

SELECT
    year,
    month,

    ROUND(revenue, 2) AS revenue,

    ROUND(
        previous_month_revenue,
        2
    ) AS previous_month_revenue,

    ROUND(
        (
            revenue -
            previous_month_revenue
        )
        /
        previous_month_revenue
        * 100,
        2
    ) AS growth_percentage

FROM revenue_growth;

-- Top 10 Products by Revenue

SELECT

    stock_code,
    description,

    SUM(quantity) AS units_sold,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM retail_transactions

WHERE is_sale = 1

GROUP BY
    stock_code,
    description

ORDER BY revenue DESC

LIMIT 10;

-- Top Products by Quantity

SELECT
    description,

    SUM(quantity) AS units_sold

FROM retail_transactions

WHERE is_sale = 1

GROUP BY description

ORDER BY units_sold DESC

LIMIT 10;

-- Revenue by Country

SELECT

    country,

    COUNT(DISTINCT invoice) AS orders,

    COUNT(DISTINCT customer_id) AS customers,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM retail_transactions

WHERE is_sale = 1

GROUP BY country

ORDER BY revenue DESC;

-- Highest-Value Customers

SELECT
    customer_id,

    COUNT(
        DISTINCT invoice
    ) AS total_orders,

    SUM(quantity) AS units_purchased,

    ROUND(
        SUM(revenue),
        2
    ) AS customer_value

FROM retail_transactions

WHERE
    is_sale = 1

    AND customer_id IS NOT NULL

GROUP BY customer_id

ORDER BY customer_value DESC

LIMIT 20;

-- Average Customer Value

WITH customer_sales AS (

    SELECT
        customer_id,

        SUM(revenue) AS customer_revenue

    FROM retail_transactions

    WHERE
        is_sale = 1
        AND customer_id IS NOT NULL

    GROUP BY customer_id
)

SELECT

    ROUND(
        AVG(customer_revenue),
        2
    ) AS average_customer_value

FROM customer_sales;

-- Repeat Customers

WITH customer_orders AS (

    SELECT
        customer_id,

        COUNT(
            DISTINCT invoice
        ) AS orders

    FROM retail_transactions

    WHERE
        is_sale = 1
        AND customer_id IS NOT NULL

    GROUP BY customer_id
)

SELECT

    COUNT(*) AS total_customers,

    SUM(
        CASE
            WHEN orders > 1
            THEN 1
            ELSE 0
        END
    ) AS repeat_customers,

    ROUND(

        SUM(
            CASE
                WHEN orders > 1
                THEN 1
                ELSE 0
            END
        )
        /
        COUNT(*)
        * 100,

        2

    ) AS repeat_customer_percentage

FROM customer_orders;

-- Sales by Day of Week

SELECT
    day_name,

    COUNT(
        DISTINCT invoice
    ) AS orders,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM retail_transactions

WHERE is_sale = 1

GROUP BY day_name

ORDER BY revenue DESC;

-- Sales by Hour

SELECT
    hour,

    COUNT(
        DISTINCT invoice
    ) AS orders,

    ROUND(
        SUM(revenue),
        2
    ) AS revenue

FROM retail_transactions

WHERE is_sale = 1

GROUP BY hour

ORDER BY hour;

-- Return Analysis

SELECT

    COUNT(*) AS return_lines,

    ABS(
        SUM(quantity)
    ) AS returned_units,

    ROUND(
        ABS(
            SUM(revenue)
        ),
        2
    ) AS returned_value

FROM retail_transactions

WHERE is_return = 1;

-- Cancellation Rate

SELECT

    COUNT(
        DISTINCT invoice
    ) AS total_invoices,

    COUNT(
        DISTINCT CASE

            WHEN is_cancelled = 1
            THEN invoice

        END
    ) AS cancelled_invoices,

    ROUND(

        COUNT(
            DISTINCT CASE

                WHEN is_cancelled = 1
                THEN invoice

            END
        )
        /
        COUNT(
            DISTINCT invoice
        )
        * 100,

        2

    ) AS cancellation_rate

FROM retail_transactions;

-- Customer RFM Analysis

WITH customer_rfm AS (

    SELECT

        customer_id,

        DATEDIFF(
            (
                SELECT
                    MAX(invoice_date)

                FROM retail_transactions
            ),

            MAX(invoice_date)

        ) AS recency,

        COUNT(
            DISTINCT invoice
        ) AS frequency,

        ROUND(
            SUM(revenue),
            2
        ) AS monetary

    FROM retail_transactions

    WHERE
        is_sale = 1

        AND customer_id IS NOT NULL

    GROUP BY customer_id
)

SELECT *

FROM customer_rfm

ORDER BY monetary DESC;