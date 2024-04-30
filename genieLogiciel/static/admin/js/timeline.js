// Function to update the timeline chart
function updateTimelineChart(stepId, active) {
    var step = document.getElementById('chartStep' + stepId);
    if (active) {
        step.classList.add('active');
    } else {
        step.classList.remove('active');
    }
    updateLines();
}

// Update the lines between dots based on active status
function updateLines() {
    var steps = document.querySelectorAll('.timeline-chart .step');
    steps.forEach((step, index) => {
        if (index < steps.length - 1) { // Don't do this for the last step
            var nextStep = steps[index + 1];
            if (step.classList.contains('active')) {
                nextStep.querySelector('.line').style.backgroundColor = '#4CAF50';
            } else {
                nextStep.querySelector('.line').style.backgroundColor = '#bbb';
            }
        }
    });
}

// Extend the existing toggleStep function
function toggleStep(stepId) {
    var checkbox = document.getElementById('customSwitch' + stepId);
    var stepIndex = Array.from(document.querySelectorAll('.custom-control-input')).indexOf(checkbox);

    // Ensure that all previous steps are checked before allowing this one to be activated
    var allPreviousChecked = true;
    document.querySelectorAll('.custom-control-input').forEach((input, index) => {
        if (index < stepIndex && !input.checked) {
            allPreviousChecked = false;
        }
    });

    if (allPreviousChecked) {
        updateTimelineChart(stepId, checkbox.checked);
    } else {
        // Uncheck the step and alert the user
        checkbox.checked = false;
        alert('Please complete previous steps first.');
    }
}
