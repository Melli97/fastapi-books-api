document.querySelectorAll('.btn-ai').forEach(button => {
    button.addEventListener('click', async function() {
        const todoTitle = this.getAttribute('data-title');
        const todoId = this.getAttribute('data-todo-id');
        const resultsDiv = document.getElementById(`ai-results-${todoId}`);
        const listContainer = document.getElementById(`subtasks-list-${todoId}`);
        
        // Stato di caricamento
        this.disabled = true;
        const originalText = this.innerHTML;
        this.innerHTML = "Elaborazione...";
        
        try {
            // Chiamata asincrona al tuo backend FastAPI
            const response = await fetch(`/ai/suggest-subtasks?todo_title=${encodeURIComponent(todoTitle)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) throw new Error("Errore di risposta dall'IA");
            
            const data = await response.json();
            
            // Svuota i risultati precedenti
            listContainer.innerHTML = '';
            
            // Inserisce i nuovi sotto-task ricevuti da Gemini
            data.subtasks.forEach(task => {
                const li = document.createElement('li');
                li.className = 'list-group-item bg-transparent py-1 px-0 border-0';
                li.innerHTML = `🔹 ${task}`;
                listContainer.appendChild(li);
            });
            
            // Mostra il rettangolo con i risultati
            resultsDiv.classList.remove('d-none');
            
        } catch (error) {
            alert("Errore: Impossibile recuperare i suggerimenti. Controlla che la chiave API sia attiva.");
            console.error(error);
        } finally {
            // Ripristina il bottone
            this.disabled = false;
            this.innerHTML = originalText;
        }
    });
});