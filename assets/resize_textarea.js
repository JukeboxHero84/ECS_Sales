if (!window.dash_clientside) { window.dash_clientside = {}; }
window.dash_clientside.clientside = {
    resizeTextarea: function(value) {
        setTimeout(function() {
            var textarea = document.getElementById('incentive-text');
            if(textarea) {
                textarea.style.height = ''; // Reset the height
                textarea.style.height = Math.min(textarea.scrollHeight, 500) + 'px';
            }
        }, 0);
        return window.dash_clientside.no_update;
    }
}
