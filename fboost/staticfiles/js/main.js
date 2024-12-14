// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    const sidebarCollapse = document.getElementById('sidebarCollapse');

    // Sidebar toggle
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('expanded');
            localStorage.setItem('sidebarState', sidebar.classList.contains('collapsed'));
        });
    }

    // Restore sidebar state
    if (localStorage.getItem('sidebarState') === 'true') {
        sidebar.classList.add('collapsed');
        content.classList.add('expanded');
    }

    // Handle mobile sidebar
    function handleResize() {
        if (window.innerWidth <= 768) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        } else {
            if (localStorage.getItem('sidebarState') !== 'true') {
                sidebar.classList.remove('collapsed');
                content.classList.remove('expanded');
            }
        }
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && 
            !sidebar.contains(event.target) && 
            !sidebarCollapse.contains(event.target)) {
            sidebar.classList.add('collapsed');
            content.classList.add('expanded');
        }
    });
});