console.log("✅ JavaScript Loaded Successfully!");

document.addEventListener("DOMContentLoaded", function () {
    const donateBtn = document.getElementById("donate-btn");
    const modal = document.getElementById("donate-modal"); // ✅ Use `id` for modal targeting
    const modalContent = document.querySelector(".modal-content");
    const closeBtn = document.querySelector(".close");

    console.log("✅ JavaScript Loaded");
    console.log("✅ Donate button found:", donateBtn);
    console.log("✅ Modal found:", modal);
    console.log("✅ Modal content found:", modalContent);

    if (!donateBtn || !modal || !modalContent || !closeBtn) {
        console.error("❌ Error: Donate button, modal, or close button not found!");
        return;
    }

    donateBtn.addEventListener("click", function () {
        console.log("✅ Donate button clicked!");

        fetch("/donate")
            .then(response => response.text())
            .then(html => {
                console.log("✅ Donation form loaded successfully!");
                modalContent.innerHTML = html;
                modal.classList.add("show");
                console.log("✅ Modal should now be visible!");
            })
            .catch(error => console.error("❌ Error loading donation form:", error));
    });

    closeBtn.addEventListener("click", function () {
        modal.classList.remove("show");
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });
});

// DONATE BUTTON
document.addEventListener("DOMContentLoaded", function () {
    const donateBtn = document.getElementById("donate-btn");
    const modal = document.getElementById("donate-modal");
    const modalContent = document.querySelector(".modal-content");
    const closeBtn = document.querySelector(".close");

    if (!donateBtn || !modal || !modalContent || !closeBtn) {
        console.error("❌ Error: Donate button, modal, or close button not found!");
        return;
    }

    // ✅ Open modal and fetch `/donate` form content
    donateBtn.addEventListener("click", function () {
        fetch("/donate")
            .then(response => response.text())
            .then(html => {
                modalContent.innerHTML = html;
                modal.classList.add("show");

                // ✅ Now that modal content is loaded, set up item description & score update
                const itemDropdown = document.getElementById("itemDropdown");
                const itemDescription = document.getElementById("itemDescription");
                const itemScore = document.getElementById("itemScore");

                if (!itemDropdown || !itemDescription || !itemScore) {
                    console.error("❌ Error: Dropdown or details fields not found after loading!");
                    return;
                }

                // ✅ Update description & score when user selects an item
                itemDropdown.addEventListener("change", function () {
                    const selectedOption = itemDropdown.options[itemDropdown.selectedIndex];
                    const description = selectedOption.getAttribute("data-description") || "No description available.";
                    const score = selectedOption.getAttribute("data-score") || "No score available.";

                    itemDescription.textContent = description;
                    itemScore.textContent = score;
                });

                // ✅ Trigger description & score update when the modal opens
                const initialSelected = itemDropdown.options[itemDropdown.selectedIndex];
                itemDescription.textContent = initialSelected.getAttribute("data-description") || "No description available.";
                itemScore.textContent = initialSelected.getAttribute("data-score") || "No score available.";
            })
            .catch(error => console.error("❌ Error loading donation form:", error));
    });

    // ✅ Close modal when clicking outside or pressing the close button
    closeBtn.addEventListener("click", function () {
        modal.classList.remove("show");
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });
});




document.addEventListener("DOMContentLoaded", function () {
// MAIN PAGE - SLIDER
    const slides = document.querySelectorAll('.slide');
    const slidesContainer = document.querySelector('.slides');
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    let currentSlide = 0;

    function updateSlider() {
        if (slides.length === 0 || !slidesContainer) {

            return;
        }
        const slideWidth = slides[0].clientWidth;
        slidesContainer.style.transform = `translateX(-${currentSlide * slideWidth}px)`;
    }

    function changeSlide(direction) {
        if (slides.length === 0) {

            return;
        }
        currentSlide += direction;
        if (currentSlide < 0) {
            currentSlide = slides.length - 1;
        } else if (currentSlide >= slides.length) {
            currentSlide = 0;
        }
        updateSlider();
    }

    if (prevButton && nextButton) {
        prevButton.addEventListener('click', () => changeSlide(-1));
        nextButton.addEventListener('click', () => changeSlide(1));
    } else {

    }

    setInterval(() => changeSlide(1), 5000);
    updateSlider();

// SIDEBAR MENU
    const menuItems = document.querySelectorAll(".sidebar-menu li a");
    const contentSections = document.querySelectorAll(".content-section");

    console.log("Menu Items Found:", menuItems.length);
    console.log("Content Sections Found:", contentSections.length);

    if (menuItems.length === 0 || contentSections.length === 0) {
        return;
    }

    menuItems.forEach(menuItem => {
        menuItem.addEventListener("click", function (event) {
            event.preventDefault();
            console.log("Clicked:", this.getAttribute("data-content"));

            menuItems.forEach(link => link.classList.remove("active"));
            this.classList.add("active");

            contentSections.forEach(section => section.style.display = "none");
            const selectedSection = document.getElementById(this.getAttribute("data-content"));
            if (selectedSection) {
                selectedSection.style.display = "block";
            } else {
                console.error("Section not found:", this.getAttribute("data-content"));
            }
        });
    });
});

menuItems.forEach(menuItem => {
    menuItem.addEventListener("click", function (event) {
        event.preventDefault();
        console.log("Clicked:", this.getAttribute("data-content"));

        menuItems.forEach(link => link.classList.remove("active"));
        this.classList.add("active");

        contentSections.forEach(section => section.style.display = "none");
        const selectedSection = document.getElementById(this.getAttribute("data-content"));

        if (selectedSection) {
            selectedSection.style.display = "block";
            console.log("Showing section:", this.getAttribute("data-content"));

            // ✅ Ensure donations section refreshes properly
            if (this.getAttribute("data-content") === "donations") {
                console.log("Loading donation data...");
                fetch("/myprofile") // Reloads Flask data
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById("donations").innerHTML = html;
                    })
                    .catch(error => console.error("❌ Error loading donations:", error));
            }
        } else {
            console.error("Section not found:", this.getAttribute("data-content"));
        }
    });
});


// LOGIN BUTTON
document.addEventListener("DOMContentLoaded", function () {
    const loginBtn = document.getElementById("login-btn");

    if (loginBtn) {
        loginBtn.addEventListener("click", function () {
            window.location.href = "/login"; // Redirects to login page
        });
    } else {
        console.error("Login button not found!");
    }
});


