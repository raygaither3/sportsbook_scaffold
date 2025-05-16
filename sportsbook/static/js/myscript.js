document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      const nav = document.querySelector('.navbar-collapse');
      if (nav.classList.contains('show')) {
        new bootstrap.Collapse(nav).toggle();
      }
    });
  });


  document.querySelectorAll('#sidebarMenu a').forEach(link => {
    link.addEventListener('click', () => {
      const sidebar = document.getElementById('sidebarMenu');
      if (window.innerWidth < 768 && sidebar.classList.contains('show')) {
        new bootstrap.Collapse(sidebar).hide();
      }
    });
  });