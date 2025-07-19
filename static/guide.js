// User Guide JavaScript

let currentStep = 1;
const totalSteps = 6;

// Initialize guide
document.addEventListener('DOMContentLoaded', function() {
    showStep(1);
    initializeAnimations();
    setupNavigation();
});

function showStep(stepNumber) {
    // Hide all steps
    const steps = document.querySelectorAll('.guide-step');
    steps.forEach(step => {
        step.classList.remove('active');
    });
    
    // Show current step
    const currentStepElement = document.getElementById(`step${stepNumber}`);
    if (currentStepElement) {
        setTimeout(() => {
            currentStepElement.classList.add('active');
            triggerStepAnimations(stepNumber);
        }, 100);
    }
    
    // Update step indicators
    updateStepIndicators(stepNumber);
    
    // Update navigation buttons
    updateNavigationButtons(stepNumber);
    
    currentStep = stepNumber;
}

function updateStepIndicators(activeStep) {
    const indicators = document.querySelectorAll('.step-dot');
    indicators.forEach((dot, index) => {
        const stepNum = index + 1;
        if (stepNum === activeStep) {
            dot.classList.add('active');
        } else {
            dot.classList.remove('active');
        }
    });
}

function updateNavigationButtons(stepNumber) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    // Update previous button
    if (stepNumber === 1) {
        prevBtn.disabled = true;
    } else {
        prevBtn.disabled = false;
    }
    
    // Update next button
    if (stepNumber === totalSteps) {
        nextBtn.textContent = 'Get Started';
        nextBtn.innerHTML = 'Get Started <i class="fas fa-rocket"></i>';
    } else {
        nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
    }
}

function setupNavigation() {
    // Previous button
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (currentStep > 1) {
            showStep(currentStep - 1);
        }
    });
    
    // Next button
    document.getElementById('nextBtn').addEventListener('click', () => {
        if (currentStep < totalSteps) {
            showStep(currentStep + 1);
        } else {
            // Redirect to main app
            window.location.href = '/';
        }
    });
    
    // Step indicators
    const stepDots = document.querySelectorAll('.step-dot');
    stepDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            showStep(index + 1);
        });
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft' && currentStep > 1) {
            showStep(currentStep - 1);
        } else if (e.key === 'ArrowRight' && currentStep < totalSteps) {
            showStep(currentStep + 1);
        } else if (e.key === 'Enter' && currentStep === totalSteps) {
            window.location.href = '/';
        }
    });
}

function triggerStepAnimations(stepNumber) {
    switch(stepNumber) {
        case 1:
            animateStep1();
            break;
        case 2:
            animateStep2();
            break;
        case 3:
            animateStep3();
            break;
        case 4:
            animateStep4();
            break;
        case 5:
            animateStep5();
            break;
        case 6:
            animateStep6();
            break;
    }
}

function animateStep1() {
    // Animate leads highlighting
    const leadRows = document.querySelectorAll('#step1 .lead-row');
    leadRows.forEach((row, index) => {
        setTimeout(() => {
            row.style.animation = 'highlight-pulse 2s ease-in-out';
        }, index * 500);
    });
}

function animateStep2() {
    // Animate context menu appearance
    const contextMenu = document.querySelector('#step2 .context-menu');
    if (contextMenu) {
        setTimeout(() => {
            contextMenu.classList.add('animated-appear');
        }, 500);
    }
}

function animateStep3() {
    // Animate text selection
    const codeLines = document.querySelectorAll('#step3 .code-line');
    codeLines.forEach((line, index) => {
        setTimeout(() => {
            line.classList.add('selected');
        }, index * 100);
    });
}

function animateStep4() {
    // Animate typing effect and button click
    const analyzeBtn = document.querySelector('#step4 .btn-analyze');
    
    setTimeout(() => {
        if (analyzeBtn) {
            analyzeBtn.classList.add('loading');
            
            setTimeout(() => {
                analyzeBtn.classList.remove('loading');
            }, 2000);
        }
    }, 1000);
}

function animateStep5() {
    // Animate dropdown selection and field mapping
    const mappingItems = document.querySelectorAll('#step5 .mapping-item');
    mappingItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.animation = 'fadeInUp 0.5s ease forwards';
        }, index * 200);
    });
}

function animateStep6() {
    // Animate extraction process
    const extractBtn = document.querySelector('#step6 .btn-extract');
    const notification = document.querySelector('#step6 .download-notification');
    
    setTimeout(() => {
        if (extractBtn) {
            extractBtn.classList.add('processing');
            
            setTimeout(() => {
                extractBtn.classList.remove('processing');
                if (notification) {
                    notification.style.animation = 'notification-appear 0.5s ease forwards';
                }
            }, 3000);
        }
    }, 500);
}

function initializeAnimations() {
    // Add CSS animations dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(30px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .animate-in {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        .animate-delay-1 { animation-delay: 0.1s; }
        .animate-delay-2 { animation-delay: 0.2s; }
        .animate-delay-3 { animation-delay: 0.3s; }
    `;
    document.head.appendChild(style);
}

// Auto-advance feature (optional)
let autoAdvanceTimer;

function startAutoAdvance() {
    autoAdvanceTimer = setInterval(() => {
        if (currentStep < totalSteps) {
            showStep(currentStep + 1);
        } else {
            stopAutoAdvance();
        }
    }, 8000); // Advance every 8 seconds
}

function stopAutoAdvance() {
    if (autoAdvanceTimer) {
        clearInterval(autoAdvanceTimer);
        autoAdvanceTimer = null;
    }
}

// Pause auto-advance on user interaction
document.addEventListener('click', stopAutoAdvance);
document.addEventListener('keydown', stopAutoAdvance);

// Touch/swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
        if (diff > 0 && currentStep < totalSteps) {
            // Swipe left - next step
            showStep(currentStep + 1);
        } else if (diff < 0 && currentStep > 1) {
            // Swipe right - previous step
            showStep(currentStep - 1);
        }
    }
}

// Intersection Observer for scroll-based animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

// Observe all animatable elements
document.querySelectorAll('.demo-screen, .step-content').forEach(el => {
    observer.observe(el);
});