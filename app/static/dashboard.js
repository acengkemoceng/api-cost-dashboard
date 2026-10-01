function formatDate(value) {
    const date = new Date(value);

    return date.toLocaleString(
        "id-ID",
        {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
        }
    );
}


function moneyTooltip(context) {
    const value = Number(
        context.raw
    );

    return (
        `${context.dataset.label}: ` +
        `$${value.toFixed(4)}`
    );
}


async function loadOpenRouterChart() {
    const canvas = document.getElementById(
        "openrouterChart"
    );

    const emptyMessage = document.getElementById(
        "openrouterChartEmpty"
    );

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

        const labels = history.map(
            (item) => formatDate(
                item.created_at
            )
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

                            data: history.map(
                                (item) =>
                                    item.usage_monthly
                            ),

                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                        },

                        {
                            label: "Total Key Usage ($)",

                            data: history.map(
                                (item) =>
                                    item.usage_total
                            ),

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
                                label: moneyTooltip,
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
            "Unable to load OpenRouter history.";

        emptyMessage.style.display = "block";
    }
}


async function loadDeepSeekChart() {
    const canvas = document.getElementById(
        "deepseekChart"
    );

    const emptyMessage = document.getElementById(
        "deepseekChartEmpty"
    );

    if (!canvas) {
        return;
    }

    try {
        const response = await fetch(
            "/api/history/deepseek?limit=30"
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

        const labels = history.map(
            (item) => formatDate(
                item.created_at
            )
        );

        new Chart(
            canvas,
            {
                type: "line",

                data: {
                    labels: labels,

                    datasets: [
                        {
                            label: "Available Balance ($)",

                            data: history.map(
                                (item) =>
                                    item.total_balance
                            ),

                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                        },

                        {
                            label: "Top-up Balance ($)",

                            data: history.map(
                                (item) =>
                                    item.topped_up_balance
                            ),

                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 4,
                        },

                        {
                            label: "Granted Credit ($)",

                            data: history.map(
                                (item) =>
                                    item.granted_balance
                            ),

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
                                label: moneyTooltip,
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
            "Failed to load DeepSeek history:",
            error
        );

        canvas.style.display = "none";

        emptyMessage.textContent =
            "Unable to load DeepSeek history.";

        emptyMessage.style.display = "block";
    }
}


document.addEventListener(
    "DOMContentLoaded",
    function () {
        loadOpenRouterChart();
        loadDeepSeekChart();
    }
);
