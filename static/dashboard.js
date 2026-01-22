
async function moveTask(taskId, destination) {
    try {
        const response = await fetch(`/task/${taskId}/move?destination=${destination}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            // Reload the page to reflect changes
            location.reload();
        } else {
            const result = await response.json();
            alert(`Error: ${result.detail || 'Failed to move task'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error connecting to server');
    }
}

// Add drag and drop functionality for task cards
document.addEventListener('DOMContentLoaded', function() {
    const draggableElements = document.querySelectorAll('.list-group-item');

    draggableElements.forEach(element => {
        element.draggable = true;

        element.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', element.querySelector('a').href.split('/').pop());
        });
    });

    const dropZones = document.querySelectorAll('.card-body.p-0');

    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            zone.style.backgroundColor = '#f8f9fa';
        });

        zone.addEventListener('dragleave', function(e) {
            zone.style.backgroundColor = '';
        });

        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            zone.style.backgroundColor = '';

            const taskId = e.dataTransfer.getData('text/plain');
            const destination = zone.closest('.card').querySelector('.card-header').textContent.trim().split(' ')[0].toLowerCase();

            if (taskId && destination) {
                moveTask(taskId, destination);
            }
        });
    });
});
