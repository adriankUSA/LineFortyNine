document.addEventListener('DOMContentLoaded', function() {
    const sideTab = document.getElementById('side-tab');
    const tabToggle = document.getElementById('tab-toggle');
  
    // Toggle the expanded state on button click
    tabToggle.addEventListener('click', () => {
      sideTab.classList.toggle('expanded');
    });
  });
  