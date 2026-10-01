async function loadOpenRouterChart() {
    const canvas = document.getElementById("openrouterChart");
    const emptyMessage = document.getElementById("chartEmpty");

    if (!canvas) {
        return;
    }

    try {
        const response = await fetch(
            "/api/history/openrouter?limit=30"
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const payload = await response.json();

        const history = payload.data
            .slice()
            .reverse();

        if (history.length === 0) {
            canvas.style.display = "none";
            emptyMessage.style.display = "block";
            return;
        }

        const labels = history.map((item) => {
            const date = new Date(item.created_at);

            return date.toLocaleString(
                "id-ID",
                {
                    day: "2-digit",
                    month: "short",
                    hour: "2-digit",
                    minute: "2-digit",
                }
            );
        });

        const monthlyUsage = history.map(
            (item) => item.usage_monthly
        );

        const totalUsage = history.map(
            (item) => item.usage_total
        );

        new Chart(
            canvas,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Monthly Usage ($)",
                            data: monthlyUsage,
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                        },
                        {
                            label: "Total Key Usage ($)",
                            data: totalUsage,
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                        },
                    ],
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    interaction: {
                        intersect: false,
                        mode: "index",
                    },

                    plugins: {
                        legend: {
                            labels: {
                                color: "#aab2bf",
                            },
                        },

                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    const value =
                                        Number(
                                            context.raw
                                        );

                                    return (
                                        `${context.dataset.label}: ` +
                                        `$${value.toFixed(6)}`
                                    );
                                },
                            },
                        },
                    },

                    scales: {
                        x: {
                            ticks: {
                                color: "#727b8a",
                                maxRotation: 0,
                            },

                            grid: {
                                color: "#1d232c",
                            },
                        },

                        y: {
                            beginAtZero: true,

                            ticks: {
                                color: "#727b8a",

                                callback: function (value) {
                                    return "$" + value;
                                },
                            },

                            grid: {
                                color: "#1d232c",
                            },
                        },
                    },
                },
            }
        );

    } catch (error) {
        console.error(
            "Failed to load OpenRouter history:",
            error
        );

        canvas.style.display = "none";
        emptyMessage.textContent =
            "Unable to load usage history.";

        emptyMessage.style.display = "block";
    }
}


document.addEventListener(
    "DOMContentLoaded",
    loadOpenRouterChart
);
