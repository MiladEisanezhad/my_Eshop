/* cart */
document.addEventListener('DOMContentLoaded', function () {
    const cartIcon = document.querySelector('.cart-wrapper');
    const cartDropdown = cartIcon.querySelector('.group-hover\\:block');

    cartIcon.addEventListener('mouseenter', function () {
        clearTimeout(cartIcon.__timer);
        cartDropdown.classList.remove('hidden');
    });

    cartIcon.addEventListener('mouseleave', function () {
        cartIcon.__timer = setTimeout(() => {
            cartDropdown.classList.add('hidden');
        }, 1300);
    });

    cartDropdown.addEventListener('mouseenter', function () {
        clearTimeout(cartIcon.__timer);
    });

    cartDropdown.addEventListener('mouseleave', function () {
        cartIcon.__timer = setTimeout(() => {
            cartDropdown.classList.add('hidden');
        }, 1300);
    });
});

/* mobile menu */
document.addEventListener("DOMContentLoaded", function () {
    const hamburgerBtn = document.getElementById('hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');

    hamburgerBtn.addEventListener('click', function () {
        mobileMenu.classList.toggle('hidden');
    });
});

/* swiper slider */
if (typeof Swiper !== 'undefined') {
    var swiper = new Swiper('.swiper', {
        slidesPerView: 2,
        loop: true,
        autoplay: {
            delay: 3000,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            1024: {
                slidesPerView: 6,
            },
        },
    });

    var swiper = new Swiper('.main-slider', {
        slidesPerView: 1,
        loop: true,
        autoplay: {
            delay: 5000,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
    });
}

/* search icon show/hide */
document.getElementById('search-icon').addEventListener('click', function () {
    var searchField = document.getElementById('search-field');
    if (searchField.classList.contains('hidden')) {
        searchField.classList.remove('hidden');
        searchField.classList.add('search-slide-down');
    } else {
        searchField.classList.add('hidden');
        searchField.classList.remove('search-slide-down');
    }
});

function toggleDropdown(id, show) {
    const dropdown = document.getElementById(id);
    if (show) {
        dropdown.classList.remove('hidden');
    } else {
        dropdown.classList.add('hidden');
    }
}

function changeImage(element) {
    var mainImage = document.getElementById('main-image');
    mainImage.src = element.getAttribute('data-full');
}

/* single page product count */
document.addEventListener('DOMContentLoaded', function () {
    const decreaseButton = document.getElementById('decrease');
    const increaseButton = document.getElementById('increase');
    const quantityInput = document.getElementById('quantity');

    if (decreaseButton && increaseButton && quantityInput) {
        decreaseButton.addEventListener('click', function () {
            let quantity = parseInt(quantityInput.value);
            if (quantity > 1) {
                quantity -= 1;
                quantityInput.value = quantity;
            }
            updateButtons();
        });

        increaseButton.addEventListener('click', function () {
            let quantity = parseInt(quantityInput.value);
            quantity += 1;
            quantityInput.value = quantity;
            updateButtons();
        });

        function updateButtons() {
            if (parseInt(quantityInput.value) === 1) {
                decreaseButton.setAttribute('disabled', true);
            } else {
                decreaseButton.removeAttribute('disabled');
            }
        }
    }
});

/* single product tabs */
document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');

    if (tabs.length > 0 && contents.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', function () {
                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                contents.forEach(c => c.classList.add('hidden'));

                this.classList.add('active');
                this.setAttribute('aria-selected', 'true');
                document.querySelector(`#${this.id.replace('-tab', '-content')}`).classList.remove('hidden');
            });
        });

        tabs[0].click();
    }
});


/* shop page filter show/hide */
document.addEventListener('DOMContentLoaded', function () {
    const toggleButton = document.getElementById('products-toggle-filters');
    const filters = document.getElementById('filters');

    if (toggleButton && filters) {
        toggleButton.addEventListener('click', function () {
            if (filters.classList.contains('hidden')) {
                filters.classList.remove('hidden');
                this.textContent = 'Hide Filters';
            } else {
                filters.classList.add('hidden');
                this.textContent = 'Show Filters';
            }
        });
    }
});

/* shop page filter*/
document.addEventListener('DOMContentLoaded', function () {
    const selectElement = document.querySelector('select');
    const arrowDown = document.getElementById('arrow-down');
    const arrowUp = document.getElementById('arrow-up');

    if (selectElement && arrowDown && arrowUp) {
        selectElement.addEventListener('click', function () {
            arrowDown.classList.toggle('hidden');
            arrowUp.classList.toggle('hidden');
        });
    }
});

/* cart page */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart-increment').forEach(button => {
        button.addEventListener('click', function () {
            let quantityElement = this.previousElementSibling;
            let quantity = parseInt(quantityElement.textContent, 10);
            quantityElement.textContent = quantity + 1;
        });
    });

    document.querySelectorAll('.cart-decrement').forEach(button => {
        button.addEventListener('click', function () {
            let quantityElement = this.nextElementSibling;
            let quantity = parseInt(quantityElement.textContent, 10);
            if (quantity > 1) {
                quantityElement.textContent = quantity - 1;
            }
        });
    });
});

// Add this code to static/js/script.js

document.addEventListener('DOMContentLoaded', () => {
    const starRatingContainer = document.getElementById('star-rating');
    
    if (!starRatingContainer) {
        return;
    }

    const stars = starRatingContainer.querySelectorAll('.rating-star');
    const inputs = starRatingContainer.querySelectorAll('.rating-input');

    // This function updates the star colors based on a given rating
    function updateStars(rating) {
        stars.forEach((star, index) => {
            if (index < rating) {
                // Use our new custom classes
                star.classList.add('is-active');
                star.classList.remove('is-inactive');
            } else {
                // Use our new custom classes
                star.classList.add('is-inactive');
                star.classList.remove('is-active');
            }
        });
    }

    // Find the currently checked radio button to get the initial rating
    let currentRating = 0;
    inputs.forEach(input => {
        if (input.checked) {
            currentRating = parseInt(input.value, 10);
        }
    });

    // Set the initial star colors when the page loads
    updateStars(currentRating);

    // Add a mouseover event to handle the hover effect
    starRatingContainer.addEventListener('mouseover', (event) => {
        const starElement = event.target.closest('.rating-star');
        if (starElement) {
            const rating = Array.from(stars).indexOf(starElement) + 1;
            updateStars(rating);
        }
    });

    // When the mouse leaves, revert to the last clicked rating
    starRatingContainer.addEventListener('mouseout', () => {
        updateStars(currentRating);
    });

    // When a star is clicked, save the new rating
    starRatingContainer.addEventListener('click', (event) => {
        const starElement = event.target.closest('.rating-star');
        if (starElement) {
            const rating = Array.from(stars).indexOf(starElement) + 1;
            currentRating = rating; // Save the new rating
            // The underlying radio button is automatically checked by the label
        }
    });
});