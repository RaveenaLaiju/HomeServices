

// Navigation bar

window.addEventListener('scroll', function() {
    if (window.scrollY >= 40) {
      document.querySelector('.navigation-bar-1').classList.add('hidden');
      document.querySelector('.navigation-bar-2').classList.remove('hidden');
    } else {
      document.querySelector('.navigation-bar-1').classList.remove('hidden');
      document.querySelector('.navigation-bar-2').classList.add('hidden');
    }
  });


  function myFunction() {
    var element = document.getElementById("myDIV");
    element.classList.toggle("mystyle");
  }


// Button submit spinner

                           




// Slide container-1
 
var swiper = new Swiper(".slide-container-1", {
  slidesPerView: 10,
  spaceBetween: 20,
  slidesPerGroup: 1, // Set to 1 to slide one group at a time
  loop: true,
  centerSlide: true,
  fade: true,
  grabCursor: true,
  pagination: {
      el: ".swiper-pagination-1",
      clickable: true,
      dynamicBullets: true,
  },
  navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
  },
  breakpoints: {
      0: {
          slidesPerView: 1,
          slidesPerGroup: 1,
      },
      520: {
          slidesPerView: 2,
          slidesPerGroup: 1,
      },
      768: {
          slidesPerView: 3,
          slidesPerGroup: 1, // Adjust here to slide one group at a time
      },
      1000: {
          slidesPerView: 5,
          slidesPerGroup: 1, // Adjust here to slide one group at a time
      },
  },
});

// slider-container-2

var swiper = new Swiper(".slide-container-2",{
  slidesPerView: 3,
  spaceBetween: 20,
  sliderPerGroup: 3,
  loop: true,
  centerSlide: "true",
  fade: "true",
  grabCursor: "true",
  pagination: {
    el: ".swiper-pagination-2",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  breakpoints: {
    0: {
      slidesPerView: 1,
    },
    520: {
      slidesPerView: 1,
    },
    768: {
      slidesPerView: 2,
    },
    1000: {
  slidesPerView: 3,
},
  },
});



// Slider-container-3

var swiper = new Swiper(".slide-container-3",{
  slidesPerView: 3,
  spaceBetween: 20,
  sliderPerGroup: 3,
  loop: true,
  centerSlide: "true",
  fade: "true",
  grabCursor: "true",
  pagination: {
    el: ".swiper-pagination-3",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  breakpoints: {
    0: {
      slidesPerView: 1,
    },
    520: {
      slidesPerView: 1,
    },
    768: {
      slidesPerView: 2,
    },
    1000: {
  slidesPerView: 3,
},
  },
});


// Slider-container-4

var swiper = new Swiper(".slide-container-4",{
  slidesPerView: 3,
  spaceBetween: 20,
  sliderPerGroup: 3,
  loop: true,
  centerSlide: "true",
  fade: "true",
  grabCursor: "true",
  pagination: {
    el: ".swiper-pagination-4",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  breakpoints: {
    0: {
      slidesPerView: 1,
    },
    520: {
      slidesPerView: 1,
    },
    768: {
      slidesPerView: 2,
    },
    1000: {
  slidesPerView: 3,
},
  },
});


// Slider-container-4
var swiper = new Swiper(".slide-container-5", {
  slidesPerView: 3,
  spaceBetween: 20,
  slidesPerGroup: 3,
  loop: true,
  centeredSlides: true,
  grabCursor: true,
  pagination: {
    el: ".swiper-pagination-5",
    clickable: true,
    dynamicBullets: true,
    bulletClass: "swiper-pagination-bullet-5",
    bulletActiveClass: "swiper-pagination-bullet-5-active"
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  breakpoints: {
    0: {
      slidesPerView: 1,
      slidesPerGroup: 1,
    },
    520: {
      slidesPerView: 1,
      slidesPerGroup: 1,
    },
    768: {
      slidesPerView: 2,
      slidesPerGroup: 2,
    },
    1000: {
      slidesPerView: 3,
      slidesPerGroup: 3,
    },
  },
});





 var swiper = new Swiper(".mySwiper", {
  slidesPerView: 3,
  spaceBetween: 50,
  grabCursor: true,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
});


  document.addEventListener('DOMContentLoaded', function() {
    // Initialize Flatpickr for time only
    flatpickr("#time", {
      enableTime: true,
      noCalendar: true,
      dateFormat: "H:i", // 24-hour format like 14:30
    });

    // Disable past dates in the date input
    document.getElementById('date').min = new Date().toISOString().split('T')[0];
  });






document.addEventListener("DOMContentLoaded", function() {
// Get all navigation links
const navLinks = document.querySelectorAll(".nav-link.nav-links");

// Get the current URL path
const currentPath = window.location.pathname;

// Iterate over all navigation links
navLinks.forEach(link => {
// Get the href attribute of the link
const linkPath = link.getAttribute("href");

// Check if the link path matches the current URL path
if (linkPath === currentPath) {
// Add the active class to the link
link.classList.add("active");
} else {
// Remove the active class if it exists
link.classList.remove("active");
}
});
});





    document.getElementById('availabilityForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const service = document.getElementById('serviceName').value;
      const location = document.getElementById('location').value;
      alert(`Checking availability for "${service}" in "${location}"`);
      const modal = bootstrap.Modal.getInstance(document.getElementById('serviceModal'));
      modal.hide();
    });
  