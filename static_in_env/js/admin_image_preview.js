document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.getElementById('image-preview-js');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview-js';
                        preview.style.maxWidth = '300px';
                        preview.style.marginTop = '10px';
                        preview.style.display = 'block';
                        // Insertar después del input
                        imageInput.parentNode.insertBefore(preview, imageInput.nextSibling);
                    }
                    preview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});
