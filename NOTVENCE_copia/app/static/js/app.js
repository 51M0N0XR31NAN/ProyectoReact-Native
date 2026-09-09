document.addEventListener("DOMContentLoaded", () => {
    animateCounters();
    setupInventoryFilters();
    setupProductForm();
    setupToastButtons();
    setupLogoutConfirmation();
    setupDeleteConfirmation();
    setupAuthToggle();
    setupGlobalSearch();
});

function showToast(message) {
    const toastElement = document.getElementById("appToast");
    const toastMessage = document.getElementById("appToastMessage");

    if (!toastElement || !toastMessage || !window.bootstrap) {
        alert(message);
        return;
    }

    toastMessage.textContent = message;
    const toast = bootstrap.Toast.getOrCreateInstance(toastElement);
    toast.show();
}

function animateCounters() {
    document.querySelectorAll("[data-counter]").forEach((counter) => {
        const target = Number(counter.dataset.counter);
        const duration = 700;
        const start = performance.now();

        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            counter.textContent = Math.round(target * progress);

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    });
}

function setupInventoryFilters() {
    const table = document.getElementById("inventoryTable");
    const search = document.getElementById("inventorySearch");
    const category = document.getElementById("categoryFilter");
    const status = document.getElementById("statusFilter");
    const clear = document.getElementById("clearFilters");
    const count = document.getElementById("inventoryCount");

    if (!table || !search || !category || !status || !clear || !count) return;

    const params = new URLSearchParams(window.location.search);
    const searchFromUrl = params.get("buscar");
    if (searchFromUrl) search.value = searchFromUrl;

    const rows = Array.from(table.querySelectorAll("tbody tr"));

    function applyFilters() {
        const text = search.value.trim().toLowerCase();
        const selectedCategory = category.value;
        const selectedStatus = status.value;
        let visible = 0;

        rows.forEach((row) => {
            const rowText = row.textContent.toLowerCase();
            const matchesText = !text || rowText.includes(text);
            const matchesCategory = !selectedCategory || row.dataset.category === selectedCategory;
            const matchesStatus = !selectedStatus || row.dataset.status === selectedStatus;
            const shouldShow = matchesText && matchesCategory && matchesStatus;

            row.classList.toggle("d-none", !shouldShow);
            if (shouldShow) visible += 1;
        });

        count.textContent = `${visible} producto${visible === 1 ? "" : "s"}`;
    }

    [search, category, status].forEach((control) => {
        control.addEventListener("input", applyFilters);
        control.addEventListener("change", applyFilters);
    });

    clear.addEventListener("click", () => {
        search.value = "";
        category.value = "";
        status.value = "";
        applyFilters();
        showToast("Filtros limpiados.");
    });

    applyFilters();
}

function setupProductForm() {
    const form = document.getElementById("productForm");
    const scanButton = document.getElementById("scanButton");
    const barcodeInput = document.getElementById("barcodeInput");
    const categorySelect = document.getElementById("categorySelect");
    const presentacionSelect = document.getElementById("presentacionSelect");

    // Función para cargar presentaciones desde la API
    const loadPresentaciones = async (categoria) => {
        if (!presentacionSelect) return;
        
        try {
            const response = await fetch(`/api/categorias/${categoria}/presentaciones`);
            const data = await response.json();
            
            // Guarda presentación actual si existe
            const currentValue = presentacionSelect.value;
            const isPlaceholder = currentValue === "" || currentValue === "Selecciona una presentación";
            
            // Limpiar opciones previas
            presentacionSelect.innerHTML = "";
            
            // Agregar nuevas opciones
            if (data.presentaciones && data.presentaciones.length > 0) {
                data.presentaciones.forEach((presentacion) => {
                    const option = document.createElement("option");
                    option.value = presentacion;
                    option.textContent = presentacion;
                    presentacionSelect.appendChild(option);
                });
                
                // Mantener la presentación actual si sigue siendo válida (ej. al editar), si no, usar la primera
                if (!isPlaceholder && data.presentaciones.includes(currentValue)) {
                    presentacionSelect.value = currentValue;
                } else {
                    presentacionSelect.value = data.presentaciones[0];
                }
            }
        } catch (error) {
            console.error("Error al cargar presentaciones:", error);
        }
    };

    // Configurar event listener para cambio de categoría
    if (categorySelect && presentacionSelect) {
        // Evento cuando cambia la categoría
        categorySelect.addEventListener("change", (e) => {
            loadPresentaciones(e.target.value);
        });

        // Cargar presentaciones iniciales inmediatamente
        loadPresentaciones(categorySelect.value);
    }

    if (form) {
        form.addEventListener("submit", (event) => {
            const requiredFields = Array.from(form.querySelectorAll("[required]"));
            const isValid = requiredFields.every((field) => field.value.trim());

            if (!isValid) {
                event.preventDefault();
                showToast("Completa los campos obligatorios.");
            }
        });
    }

    if (scanButton && barcodeInput) {
        scanButton.addEventListener("click", () => {
            barcodeInput.value = `770${Math.floor(1000000000 + Math.random() * 8999999999)}`;
            showToast("Código escaneado de prueba.");
        });
    }
}

function setupToastButtons() {
    document.querySelectorAll("[data-toast]").forEach((button) => {
        button.addEventListener("click", () => showToast(button.dataset.toast));
    });
}

function setupLogoutConfirmation() {
    const logout = document.querySelector("[data-confirm-logout]");

    if (!logout) return;

    logout.addEventListener("click", (event) => {
        if (!confirm("¿Deseas cerrar sesión?")) {
            event.preventDefault();
        }
    });
}

function setupDeleteConfirmation() {
    document.querySelectorAll("[data-confirm-delete]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!confirm("¿Deseas eliminar este producto?")) {
                event.preventDefault();
            }
        });
    });
}

function toggleAuthForm(mode) {
    const shell = document.querySelector(".auth-form-shell");
    const optionButtons = document.querySelectorAll(".auth-option");
    const formPanels = {
        login: document.getElementById("loginFormPanel"),
        register: document.getElementById("registerFormPanel")
    };

    if (!shell || !formPanels.login || !formPanels.register) return;

    shell.classList.remove("hidden");
    shell.style.display = "block";

    optionButtons.forEach((button) => {
        const isActive = button.dataset.auth === mode;
        button.classList.toggle("active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
        button.setAttribute("aria-selected", String(isActive));
    });

    Object.entries(formPanels).forEach(([key, panel]) => {
        const shouldShow = key === mode;
        panel.style.display = shouldShow ? "block" : "none";
        panel.classList.toggle("is-hidden", !shouldShow);
        if (shouldShow) {
            panel.querySelector("input")?.focus();
        }
    });
}

function setupAuthToggle() {
    const shell = document.querySelector(".auth-form-shell");
    const optionButtons = document.querySelectorAll(".auth-option");
    const formPanels = {
        login: document.getElementById("loginFormPanel"),
        register: document.getElementById("registerFormPanel")
    };

    if (!optionButtons.length || !formPanels.login || !formPanels.register) return;

    shell?.classList.add("hidden");
    shell && (shell.style.display = "none");

    Object.values(formPanels).forEach((panel) => {
        panel.style.display = "none";
        panel.classList.add("is-hidden");
    });

    const initialMode = document.querySelector(".auth-option.active")?.dataset.auth || "login";
    toggleAuthForm(initialMode);

    optionButtons.forEach((button) => {
        button.addEventListener("click", () => toggleAuthForm(button.dataset.auth));
    });
}

function setupGlobalSearch() {
    const globalSearch = document.getElementById("globalSearch");
    if (!globalSearch) return;

    const routes = [
        { keywords: ["inventario", "producto", "productos", "buscar"], url: "/inventario" },
        { keywords: ["registrar", "nuevo", "agregar", "crear"], url: "/producto/nuevo" },
        { keywords: ["alerta", "alertas", "vencimiento", "vencidos"], url: "/alertas" },
    ];

    globalSearch.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") return;

        event.preventDefault();
        const query = globalSearch.value.trim().toLowerCase();
        if (!query) return;

        const match = routes.find((route) => route.keywords.some((keyword) => query.includes(keyword)));

        if (match) {
            window.location.href = match.url;
            return;
        }

        window.location.href = `/inventario?buscar=${encodeURIComponent(query)}`;
    });
}
