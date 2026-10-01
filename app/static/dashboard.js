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


function activateTab(name) {
    const buttons = document.querySelectorAll(
        "[data-tab-target]"
    );

    const panels = document.querySelectorAll(
        "[data-tab-panel]"
    );

    buttons.forEach((button) => {
        button.classList.toggle(
            "active",
            button.dataset.tabTarget === name
        );
    });

    panels.forEach((panel) => {
        panel.classList.toggle(
            "active",
            panel.dataset.tabPanel === name
        );
    });
}


function setupTabs() {
    const buttons = document.querySelectorAll(
        "[data-tab-target]"
    );

    buttons.forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                const target =
                    button.dataset.tabTarget;

                window.location.hash =
                    target;

                activateTab(
                    target
                );
            }
        );

    });

    const hash =
        window.location.hash
            .replace("#", "");

    const allowed = [
        "overview",
        "openrouter",
        "deepseek",
        "integrations",
    ];

    activateTab(
        allowed.includes(hash)
            ? hash
            : "overview"
    );
}


async function loadOpenRouterChart() {
    const canvas = document.getElementById(
        "openrouterChart"
    );

    const empty = document.getElementById(
        "openrouterChartEmpty"
    );

    if (!canvas) {
        return;
    }

    try {
        const response = await fetch(
            "/api/history/openrouter?limit=50"
        );

        const payload =
            await response.json();

        const history = payload.data
            .slice()
            .reverse();

        if (!history.length) {
            canvas.style.display = "none";
            empty.style.display = "block";
            return;
        }

        new Chart(
            canvas,
            {
                type: "line",

                data: {
                    labels: history.map(
                        (item) =>
                            formatDate(
                                item.created_at
                            )
                    ),

                    datasets: [
                        {
                            label:
                                "Monthly Usage ($)",

                            data: history.map(
                                (item) =>
                                    item.usage_monthly
                            ),

                            tension: 0.3,
                            borderWidth: 2,
                        },

                        {
                            label:
                                "Total Key Usage ($)",

                            data: history.map(
                                (item) =>
                                    item.usage_total
                            ),

                            tension: 0.3,
                            borderWidth: 2,
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
                                label:
                                    moneyTooltip,
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
            error
        );

        canvas.style.display = "none";
        empty.style.display = "block";
    }
}


async function loadDeepSeekChart() {
    const canvas = document.getElementById(
        "deepseekChart"
    );

    const empty = document.getElementById(
        "deepseekChartEmpty"
    );

    if (!canvas) {
        return;
    }

    try {
        const response = await fetch(
            "/api/history/deepseek?limit=50"
        );

        const payload =
            await response.json();

        const history = payload.data
            .slice()
            .reverse();

        if (!history.length) {
            canvas.style.display = "none";
            empty.style.display = "block";
            return;
        }

        new Chart(
            canvas,
            {
                type: "line",

                data: {
                    labels: history.map(
                        (item) =>
                            formatDate(
                                item.created_at
                            )
                    ),

                    datasets: [
                        {
                            label:
                                "Available Balance ($)",

                            data: history.map(
                                (item) =>
                                    item.total_balance
                            ),

                            tension: 0.3,
                            borderWidth: 2,
                        },

                        {
                            label:
                                "Top-up Balance ($)",

                            data: history.map(
                                (item) =>
                                    item.topped_up_balance
                            ),

                            tension: 0.3,
                            borderWidth: 2,
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
                                label:
                                    moneyTooltip,
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
            error
        );

        canvas.style.display = "none";
        empty.style.display = "block";
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupTabs();

        loadOpenRouterChart();
        loadDeepSeekChart();

    }
);
