document.addEventListener("DOMContentLoaded", function () {
  const slidePage = document.querySelector(".slide-page");
  const pages = document.querySelectorAll(".page");
  const nextBtns = document.querySelectorAll(".next");
  const prevBtns = document.querySelectorAll(".prev");
  const submitBtn = document.querySelector(".submit");

  const progressText = document.querySelectorAll(".step p");
  const progressCheck = document.querySelectorAll(".step .check");
  const bullet = document.querySelectorAll(".step .bullet");

  let currentStep = 0;

  function validateFields(stepIndex) {
      const inputs = pages[stepIndex].querySelectorAll("input, select");
      let isValid = true;

      inputs.forEach(input => {
          if (!input.value.trim()) {
              isValid = false;
              input.classList.add("error"); // Highlight empty fields
          } else {
              input.classList.remove("error");
          }
      });

      return isValid;
  }

  function toggleNextButton(stepIndex) {
      const nextBtn = pages[stepIndex].querySelector(".next");
      if (nextBtn) {
          nextBtn.disabled = !validateFields(stepIndex);
      }
  }

  function moveNext() {
      if (validateFields(currentStep)) {
          currentStep += 1;
          slidePage.style.marginLeft = `-${currentStep * 25}%`;

          bullet[currentStep - 1].classList.add("active");
          progressCheck[currentStep - 1].classList.add("active");
          progressText[currentStep - 1].classList.add("active");

          if (currentStep === pages.length - 1) {
              submitBtn.disabled = false; // Enable submit on last step
          }
      }
  }

  function movePrev() {
      currentStep -= 1;
      slidePage.style.marginLeft = `-${currentStep * 25}%`;

      bullet[currentStep].classList.remove("active");
      progressCheck[currentStep].classList.remove("active");
      progressText[currentStep].classList.remove("active");

      submitBtn.disabled = true; // Disable submit when going back
  }

  nextBtns.forEach((btn, index) => {
      btn.disabled = true; // Hide Next button initially
      btn.addEventListener("click", function (event) {
          event.preventDefault();
          moveNext();
      });

      const inputs = pages[index].querySelectorAll("input, select");
      inputs.forEach(input => {
          input.addEventListener("input", function () {
              toggleNextButton(index);
          });

          if (input.tagName === "SELECT") {
              input.addEventListener("change", function () {
                  toggleNextButton(index);
              });
          }
      });
  });

  prevBtns.forEach((btn) => {
      btn.addEventListener("click", function (event) {
          event.preventDefault();
          movePrev();
      });
  });

  submitBtn.disabled = true; // Disable submit initially
  submitBtn.addEventListener("click", function (event) {
      if (validateFields(currentStep)) {
          bullet[currentStep].classList.add("active");
          progressCheck[currentStep].classList.add("active");
          progressText[currentStep].classList.add("active");

          alert("Your Form Successfully Signed Up!"); 
          document.querySelector("form").submit(); // Submit the form properly
      } else {
          event.preventDefault();
      }
  });

  for (let i = 0; i < nextBtns.length; i++) {
      toggleNextButton(i);
  }
});
