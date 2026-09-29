// =========================================================
// API helper
// =========================================================

async function postJSON(
    url,
    data
) {

    const response =
        await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                credentials: "include",
                body: JSON.stringify(data)
            }
        );

    const result =
        await response.json();

    if (!response.ok) {

        throw new Error(
            result.detail ||
            "Unable to generate recommendations."
        );
    }

    return result;
}


// =========================================================
// Render recommendations
// =========================================================

function renderResults(
    result,
    container
) {

    container.classList.remove(
        "hidden"
    );

    const allocationEntries =
        Object.entries(
            result.allocation || {}
        );

    const allocationHtml =
        allocationEntries.length
            ? `
                <div class="allocation-grid">

                    ${allocationEntries
                        .map(
                            ([key, value]) => `
                                <div class="allocation-card">
                                    <span>
                                        ${escapeHtml(
                                            key
                                        )}
                                    </span>

                                    <strong>
                                        ${formatCurrency(
                                            value
                                        )}
                                    </strong>
                                </div>
                            `
                        )
                        .join("")}

                </div>
            `
            : "";


    const itemsHtml =
        (result.items || [])
            .map(
                item => `
                    <article class="recommendation-card">

                        <div class="recommendation-category">
                            ${escapeHtml(
                                item.category
                            )}
                        </div>

                        <h3>
                            ${escapeHtml(
                                item.name
                            )}
                        </h3>

                        <div class="recommendation-price">
                            ${formatCurrency(
                                item.estimated_price
                            )}
                        </div>

                        <p>
                            ${escapeHtml(
                                item.reason
                            )}
                        </p>

                        <div class="recommendation-footer">

                            <span>
                                ${escapeHtml(
                                    item.platform
                                )}
                            </span>

                            <a
                                href="${item.search_url}"
                                target="_blank"
                                rel="noopener noreferrer"
                                class="btn btn-small btn-secondary"
                            >
                                Search
                            </a>

                        </div>

                    </article>
                `
            )
            .join("");


    const tipsHtml =
        (result.tips || [])
            .map(
                tip => `
                    <li>
                        ${escapeHtml(tip)}
                    </li>
                `
            )
            .join("");


    container.innerHTML = `

        <div class="results-header">

            <div>

                <span class="eyebrow">
                    Your AI plan
                </span>

                <h2>
                    Recommendations
                </h2>

            </div>

            <div class="result-budget">

                <small>
                    Budget
                </small>

                <strong>
                    ${formatCurrency(
                        result.budget
                    )}
                </strong>

            </div>

        </div>


        <div class="summary-card">

            <div class="summary-icon">
                ✦
            </div>

            <div>

                <strong>
                    ${escapeHtml(
                        result.summary
                    )}
                </strong>

                <p>
                    ${
                        result.source_mode === "gemini"
                            ? "Generated with Gemini AI."
                            : "Generated with PocketSmart AI fallback recommendations."
                    }
                </p>

            </div>

        </div>


        ${allocationHtml}


        <div class="recommendation-grid">

            ${itemsHtml}

        </div>


        <div class="tips-card">

            <h3>
                Smart spending tips
            </h3>

            <ul>
                ${tipsHtml}
            </ul>

        </div>

    `;
}


// =========================================================
// Loading
// =========================================================

function setLoading(
    button,
    loading
) {

    if (!button) {
        return;
    }

    if (loading) {

        button.disabled = true;

        button.dataset.originalText =
            button.textContent;

        button.textContent =
            "Generating...";

    } else {

        button.disabled = false;

        button.textContent =
            button.dataset.originalText ||
            "Generate Recommendations";
    }
}


// =========================================================
// Login requirement
// =========================================================

async function ensureLoggedIn() {

    const response =
        await fetch(
            "/api/session-info",
            {
                credentials: "include"
            }
        );

    if (!response.ok) {

        showToast(
            "Please login before creating a plan.",
            "error"
        );

        setTimeout(
            () => {
                window.location.href =
                    "/login";
            },
            900
        );

        return false;
    }

    return true;
}


// =========================================================
// Home planner
// =========================================================

function setupHomePlanner() {

    const form =
        document.getElementById(
            "home-form"
        );

    const results =
        document.getElementById(
            "results"
        );

    if (!form || !results) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            if (!await ensureLoggedIn()) {
                return;
            }

            const budget =
                Number(
                    form.budget.value
                );

            const rooms =
                Array.from(
                    form.querySelectorAll(
                        'input[name="rooms"]:checked'
                    )
                )
                .map(
                    checkbox =>
                        checkbox.value
                );

            const priorities =
                Array.from(
                    form.querySelectorAll(
                        'input[name="priorities"]:checked'
                    )
                )
                .map(
                    checkbox =>
                        checkbox.value
                );

            if (!rooms.length) {

                showToast(
                    "Select at least one room.",
                    "error"
                );

                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                setLoading(
                    button,
                    true
                );

                const result =
                    await postJSON(
                        "/api/generate-home",
                        {
                            budget,
                            rooms,
                            style: form.style.value,
                            priorities,
                            notes: form.notes.value
                        }
                    );

                renderResults(
                    result,
                    results
                );

                results.scrollIntoView({
                    behavior: "smooth"
                });

            } catch (error) {

                showToast(
                    error.message,
                    "error"
                );

            } finally {

                setLoading(
                    button,
                    false
                );
            }
        }
    );
}


// =========================================================
// Party planner
// =========================================================

function setupPartyPlanner() {

    const form =
        document.getElementById(
            "party-form"
        );

    const results =
        document.getElementById(
            "results"
        );

    if (!form || !results) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            if (!await ensureLoggedIn()) {
                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                setLoading(
                    button,
                    true
                );

                const result =
                    await postJSON(
                        "/api/generate-party",
                        {
                            budget:
                                Number(
                                    form.budget.value
                                ),

                            guests:
                                Number(
                                    form.guests.value
                                ),

                            event_type:
                                form.event_type.value,

                            city:
                                form.city.value,

                            venue:
                                form.venue.value,

                            food_preference:
                                form.food_preference.value,

                            notes:
                                form.notes.value
                        }
                    );

                renderResults(
                    result,
                    results
                );

                results.scrollIntoView({
                    behavior: "smooth"
                });

            } catch (error) {

                showToast(
                    error.message,
                    "error"
                );

            } finally {

                setLoading(
                    button,
                    false
                );
            }
        }
    );
}


// =========================================================
// Jewelry planner
// =========================================================

function setupJewelryPlanner() {

    const form =
        document.getElementById(
            "jewelry-form"
        );

    const results =
        document.getElementById(
            "results"
        );

    if (!form || !results) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            if (!await ensureLoggedIn()) {
                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            try {

                setLoading(
                    button,
                    true
                );

                const formData =
                    new FormData();

                formData.append(
                    "budget",
                    form.budget.value
                );

                formData.append(
                    "occasion",
                    form.occasion.value
                );

                formData.append(
                    "style",
                    form.style.value
                );

                formData.append(
                    "metal",
                    form.metal.value
                );

                formData.append(
                    "notes",
                    form.notes.value
                );

                const image =
                    form.outfit_image.files[0];

                if (image) {

                    formData.append(
                        "outfit_image",
                        image
                    );
                }

                const response =
                    await fetch(
                        "/api/generate-jewelry",
                        {
                            method: "POST",
                            credentials: "include",
                            body: formData
                        }
                    );

                const result =
                    await response.json();

                if (!response.ok) {

                    throw new Error(
                        result.detail ||
                        "Unable to generate jewelry recommendations."
                    );
                }

                renderResults(
                    result,
                    results
                );

                results.scrollIntoView({
                    behavior: "smooth"
                });

            } catch (error) {

                showToast(
                    error.message,
                    "error"
                );

            } finally {

                setLoading(
                    button,
                    false
                );
            }
        }
    );
}
