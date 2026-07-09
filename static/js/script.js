console.log('🚀 JavaScript loaded!');

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded');
    
    // Get elements
    const languageSelect = document.getElementById('language');
    const codeInput = document.getElementById('codeInput');
    const explainBtn = document.getElementById('explainBtn');
    const clearBtn = document.getElementById('clearBtn');
    const responseContainer = document.getElementById('responseContainer');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    // Check if elements exist
    console.log('🔍 Elements found:', {
        languageSelect: !!languageSelect,
        codeInput: !!codeInput,
        explainBtn: !!explainBtn,
        clearBtn: !!clearBtn,
        responseContainer: !!responseContainer,
        loadingSpinner: !!loadingSpinner
    });
    
    // Explain Code Button Click
    if (explainBtn) {
        explainBtn.addEventListener('click', async function() {
            console.log('🔄 Explain button clicked!');
            
            const code = codeInput ? codeInput.value.trim() : '';
            const language = languageSelect ? languageSelect.value : 'python';
            
            console.log('📝 Code length:', code.length);
            console.log('🌐 Language:', language);
            
            if (!code) {
                alert('⚠️ Please paste some code to analyze.');
                return;
            }
            
            // Show loading
            if (loadingSpinner) loadingSpinner.style.display = 'block';
            if (responseContainer) {
                responseContainer.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: #6366f1;">
                        <p>⏳ AI is thinking...</p>
                    </div>
                `;
            }
            if (explainBtn) {
                explainBtn.disabled = true;
                explainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
            
            try {
                console.log('📤 Sending request to /api/explain-code');
                
                const response = await fetch('/api/explain-code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        code: code,
                        language: language
                    })
                });
                
                console.log('📥 Response status:', response.status);
                
                const data = await response.json();
                console.log('📦 Response data:', data);
                
                // Hide loading
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (explainBtn) {
                    explainBtn.disabled = false;
                    explainBtn.innerHTML = '<i class="fas fa-robot"></i> Explain Code';
                }
                
                if (data.success) {
                    if (responseContainer) {
                        responseContainer.innerHTML = data.explanation;
                    }
                    console.log('✅ Explanation displayed!');
                } else {
                    if (responseContainer) {
                        responseContainer.innerHTML = `
                            <div style="background: #fee2e2; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444;">
                                <h4 style="color: #dc2626; margin: 0;">
                                    <i class="fas fa-exclamation-circle"></i> Error
                                </h4>
                                <p style="color: #991b1b; margin: 5px 0 0 0;">${data.error || 'Something went wrong'}</p>
                            </div>
                        `;
                    }
                }
                
            } catch (error) {
                console.error('❌ Error:', error);
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (explainBtn) {
                    explainBtn.disabled = false;
                    explainBtn.innerHTML = '<i class="fas fa-robot"></i> Explain Code';
                }
                
                if (responseContainer) {
                    responseContainer.innerHTML = `
                        <div style="background: #fee2e2; padding: 20px; border-radius: 8px; border-left: 4px solid #ef4444;">
                            <h4 style="color: #dc2626; margin: 0;">
                                <i class="fas fa-exclamation-circle"></i> Network Error
                            </h4>
                            <p style="color: #991b1b; margin: 5px 0 0 0;">${error.message || 'Please check your connection'}</p>
                        </div>
                    `;
                }
            }
        });
    }
    
    // Clear Button
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            console.log('🧹 Clear button clicked');
            if (codeInput) codeInput.value = '';
            if (responseContainer) {
                responseContainer.innerHTML = `
                    <div style="text-align:center;color:#94a3b8;padding:3rem 1rem;">
                        <i class="fas fa-robot" style="font-size:48px;color:#94a3b8;"></i>
                        <p>Your code explanation will appear here</p>
                        <p style="font-size:0.875rem;margin-top:0.5rem;">Select a language, paste your code, and click "Explain Code"</p>
                    </div>
                `;
            }
        });
    }
    
    // Ctrl+Enter shortcut
    if (codeInput) {
        codeInput.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                console.log('⌨️ Ctrl+Enter pressed');
                if (explainBtn) explainBtn.click();
            }
        });
    }
    
    console.log('✅ JavaScript ready!');
});