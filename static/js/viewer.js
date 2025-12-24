// static/js/viewer.js
class NovelViewer {
    constructor() {
        this.currentSceneIndex = 0;
        this.scenesData = [];
        this.init();
    }
    
    init() {
        console.log(' Инициализация читалки новелл');
        
        const novelData = this.loadNovelData();
        this.scenesData = novelData.scenes || [];
        
        console.log('Загружены сцены:', this.scenesData);
        
        if (this.scenesData.length > 0) {
            this.displayScene(0);
            document.getElementById('total-scenes').textContent = this.scenesData.length;
        } else {
            this.showNoScenesMessage();
        }
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Навигация
        document.getElementById('prev-btn')?.addEventListener('click', () => this.prevScene());
        document.getElementById('next-btn')?.addEventListener('click', () => this.nextScene());
        
        // Кнопки в конце истории
        document.querySelectorAll('.end-message .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (e.target.textContent.includes('Начать заново')) {
                    this.displayScene(0);
                }
            });
        });
    }
    
    loadNovelData() {
        try {
            const dataElement = document.getElementById('novel-data');
            if (!dataElement) {
                console.error('Element with novel data not found');
                return { scenes: [] };
            }
            
            const jsonText = dataElement.textContent.trim();
            if (!jsonText) {
                console.error('No JSON data found');
                return { scenes: [] };
            }
            
            return JSON.parse(jsonText);
        } catch (error) {
            console.error('Error parsing novel data:', error);
            return { scenes: [] };
        }
    }
    
    displayScene(index) {
        if (index < 0 || index >= this.scenesData.length) {
            this.showEndMessage();
            return;
        }
        
        this.currentSceneIndex = index;
        const scene = this.scenesData[index];
        
        // Обновляем заголовок
        document.getElementById('current-scene').textContent = index + 1;
        
        // Очищаем контейнер спрайтов
        const spritesContainer = document.getElementById('scene-sprites-container');
        spritesContainer.innerHTML = '';
        
        // Фон сцены
        if (scene.background) {
            const background = document.createElement('div');
            background.className = 'scene-background';
            background.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url('${this.escapeHtml(scene.background)}');
                background-size: cover;
                background-position: center;
            `;
            spritesContainer.appendChild(background);
        }
        
        // Спрайты персонажей
        if (scene.sprites && Array.isArray(scene.sprites)) {
            scene.sprites.forEach(sprite => {
                if (sprite.isOnCanvas !== false && sprite.url) {
                    const spriteElement = document.createElement('div');
                    spriteElement.className = 'sprite-item';
                    spriteElement.style.cssText = `
                        position: absolute;
                        left: ${sprite.x || 100}px;
                        top: ${sprite.y || 100}px;
                        width: ${sprite.width || 150}px;
                        height: ${sprite.height || 200}px;
                        transform: rotate(${sprite.rotation || 0}deg);
                        z-index: ${sprite.zIndex || 1};
                    `;
                    
                    spriteElement.innerHTML = `
                        <img src="${this.escapeHtml(sprite.url)}" alt="${sprite.name || 'Спрайт'}" 
                             class="sprite-image"
                             onerror="this.style.display='none'">
                    `;
                    
                    spritesContainer.appendChild(spriteElement);
                }
            });
        }
        
        // Текст сцены
        const sceneText = scene.text ? scene.text.replace(/\n/g, '<br>') : '...';
        const sceneName = scene.name ? `<h3>${this.escapeHtml(scene.name)}</h3>` : '';
        
        document.getElementById('scene-display').innerHTML = sceneName + `
            <div class="scene-text">
                ${sceneText}
            </div>
        `;
        
        // Отображаем варианты выбора
        this.displayChoices(scene.choices);
        
        // Обновляем прогресс
        this.updateProgress(index);
        
        // Обновляем навигацию
        this.updateNavigation(index, scene.choices);
        
        // Прокручиваем наверх
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    displayChoices(choices) {
        const choicesContainer = document.getElementById('choices-display');
        
        if (!choices || choices.length === 0) {
            choicesContainer.innerHTML = '';
            return;
        }
        
        let choicesHTML = '<h3>Ваш выбор:</h3>';
        
        choices.forEach((choice, index) => {
            const choiceText = choice.text || `Вариант ${index + 1}`;
            const nextScene = choice.nextScene || 0;
            
            if (nextScene === 0) {
                choicesHTML += `
                    <button class="choice-btn choice-end" onclick="novelViewer.showEndMessage('🎉 ${this.escapeHtml(choiceText)}')">
                        ${this.escapeHtml(choiceText)}
                    </button>
                `;
            } else if (nextScene > 0 && nextScene <= this.scenesData.length) {
                choicesHTML += `
                    <button class="choice-btn" onclick="novelViewer.goToScene(${nextScene - 1})">
                        ${this.escapeHtml(choiceText)}
                    </button>
                `;
            } else {
                choicesHTML += `
                    <button class="choice-btn" onclick="novelViewer.nextScene()">
                        ${this.escapeHtml(choiceText)}
                    </button>
                `;
            }
        });
        
        choicesContainer.innerHTML = choicesHTML;
    }
    
    updateProgress(index) {
        const progress = ((index + 1) / this.scenesData.length) * 100;
        document.getElementById('progress-bar').style.width = `${progress}%`;
        document.getElementById('progress-percent').textContent = `${Math.round(progress)}%`;
    }
    
    updateNavigation(index, choices) {
        const prevBtn = document.getElementById('prev-btn');
        const nextBtn = document.getElementById('next-btn');
        
        prevBtn.style.display = index > 0 ? 'block' : 'none';
        
        const hasChoices = choices && choices.length > 0;
        const hasNextScene = index < this.scenesData.length - 1;
        
        nextBtn.style.display = (!hasChoices && hasNextScene) ? 'block' : 'none';
    }
    
    goToScene(index) {
        if (index >= 0 && index < this.scenesData.length) {
            this.displayScene(index);
        } else {
            this.showEndMessage();
        }
    }
    
    nextScene() {
        if (this.currentSceneIndex < this.scenesData.length - 1) {
            this.displayScene(this.currentSceneIndex + 1);
        } else {
            this.showEndMessage();
        }
    }
    
    prevScene() {
        if (this.currentSceneIndex > 0) {
            this.displayScene(this.currentSceneIndex - 1);
        }
    }
    
    showEndMessage(customMessage = null) {
        const message = customMessage || ' Поздравляем! Вы дочитали новеллу до конца.';
        
        document.getElementById('scene-sprites-container').innerHTML = '';
        document.getElementById('scene-display').innerHTML = `
            <div class="end-message">
                <h3>Конец истории</h3>
                <p>${message}</p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button onclick="novelViewer.displayScene(0)" class="btn btn-primary">
                         Начать заново
                    </button>
                    <button onclick="window.location.href='/'" class="btn btn-secondary">
                         На главную
                    </button>
                    <button onclick="window.location.href='/builder'" class="btn btn-success">
                         Создать свою
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('choices-display').innerHTML = '';
        document.getElementById('prev-btn').style.display = 'none';
        document.getElementById('next-btn').style.display = 'none';
        document.getElementById('progress-bar').style.width = '100%';
        document.getElementById('progress-percent').textContent = '100%';
    }
    
    showNoScenesMessage() {
        document.getElementById('scene-display').innerHTML = `
            <div class="error-message">
                <h3>В этой новелле пока нет сцен</h3>
                <p>Автор ещё не добавил содержание.</p>
                <button onclick="window.location.href='/'" class="btn btn-primary">
                    ← Вернуться на главную
                </button>
            </div>
        `;
        
        document.getElementById('choices-display').innerHTML = '';
        document.getElementById('prev-btn').style.display = 'none';
        document.getElementById('next-btn').style.display = 'none';
    }
    
    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    window.novelViewer = new NovelViewer();
});