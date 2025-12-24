// static/js/builder.js
class NovelBuilder {
    constructor(novelId) {
        this.novelId = novelId;
        this.scenes = [];
        this.currentSceneIndex = -1;
        this.currentSprites = [];
        this.choices = [];
        this.activeTool = 'select';
        this.draggingSprite = null;
        
        console.log("🚀 Конструктор инициализирован, ID новеллы:", this.novelId);
        
        this.init();
    }
    
    init() {
        if (this.novelId && this.novelId > 0) {
            console.log("🔄 Загружаю данные новеллы...");
            this.loadNovelData();
            this.setupEventListeners();
            this.setupDragAndDrop();
        } else if (this.novelId === 0 && window.location.pathname.includes('/builder/')) {
            console.log("⚠️ Нет ID новеллы, перенаправляю...");
            window.location.href = '/builder';
        }
    }
    
    setupEventListeners() {
        // Загрузка фона
        document.getElementById('background-upload-area')?.addEventListener('click', () => {
            document.getElementById('background-file').click();
        });
        
        document.getElementById('background-file')?.addEventListener('change', (e) => {
            this.handleBackgroundFile(e.target.files);
        });
        
        // Загрузка спрайтов
        document.getElementById('sprite-upload-area')?.addEventListener('click', () => {
            document.getElementById('sprite-file').click();
        });
        
        document.getElementById('sprite-file')?.addEventListener('change', (e) => {
            this.handleSpriteFiles(e.target.files);
        });
        
        // Сохранение новеллы
        document.getElementById('save-btn')?.addEventListener('click', () => {
            this.saveNovel();
        });
        
        // Сохранение сцены
        document.getElementById('save-scene-btn')?.addEventListener('click', () => {
            this.saveCurrentScene();
        });
        
        // Публикация
        document.getElementById('publish-btn')?.addEventListener('click', () => {
            this.publishNovel();
        });
        
        // Предпросмотр
        document.getElementById('preview-btn')?.addEventListener('click', () => {
            this.previewNovel();
        });
        
        // Добавление новой сцены
        const addSceneButtons = [
            document.getElementById('add-scene-btn'),
            document.getElementById('add-scene-btn-bottom')
        ];
        
        addSceneButtons.forEach(btn => {
            btn?.addEventListener('click', () => {
                this.addNewScene();
            });
        });
        
        // Добавление выбора
        document.getElementById('add-choice-btn')?.addEventListener('click', () => {
            this.addNewChoice();
        });
        
        // Инструменты
        document.querySelectorAll('.tool-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tool = e.currentTarget.getAttribute('data-tool');
                this.selectTool(tool);
            });
        });
        
        // Изменение названия новеллы
        document.getElementById('novel-title')?.addEventListener('input', (e) => {
            this.updateNovelTitle(e.target.value);
        });
        
        // Публикация чекбокс
        document.getElementById('novel-published')?.addEventListener('change', (e) => {
            this.updatePublishStatus(e.target.checked);
        });
    }
    
    setupDragAndDrop() {
        const canvas = document.getElementById('scene-canvas');
        const spriteUploadArea = document.getElementById('sprite-upload-area');
        const backgroundUploadArea = document.getElementById('background-upload-area');
        
        // Drag & Drop для спрайтов
        spriteUploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        });
        
        spriteUploadArea?.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
        });
        
        spriteUploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            this.handleSpriteDrop(e);
        });
        
        // Drag & Drop для фона
        backgroundUploadArea?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        });
        
        backgroundUploadArea?.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
        });
        
        backgroundUploadArea?.addEventListener('drop', (e) => {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            this.handleBackgroundDrop(e);
        });
        
        // Drag & Drop на холст
        canvas?.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        });
        
        canvas?.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropOnCanvas(e);
        });
    }
    
    async loadNovelData() {
        try {
            console.log(`📡 Запрос данных новеллы ${this.novelId}...`);
            this.showLoading();
            
            const response = await fetch(`/api/novel/${this.novelId}`);
            if (!response.ok) {
                throw new Error('Ошибка загрузки данных');
            }
            
            const data = await response.json();
            
            console.log("📦 Получены данные:", data);
            
            if (data.error) {
                this.showNotification('❌ Ошибка загрузки: ' + data.error, 'error');
                return;
            }
            
            this.scenes = data.scenes || [];
            console.log(`📚 Загружено ${this.scenes.length} сцен:`, this.scenes);
            
            // Обновляем UI
            this.updateNovelTitle(data.title);
            document.getElementById('novel-title').value = data.title || '';
            document.getElementById('novel-description').value = data.description || '';
            document.getElementById('novel-published').checked = data.is_published || false;
            this.updatePublishStatus(data.is_published);
            
            // Рендерим сцены
            this.renderSceneList();
            
            // Если есть сцены, показываем первую
            if (this.scenes.length > 0) {
                console.log("🎯 Выбираю первую сцену");
                this.selectScene(0);
            } else {
                console.log("➕ Нет сцен, создаю первую");
                this.addNewScene();
            }
            
            console.log("✅ Данные успешно загружены");
            
        } catch (error) {
            console.error('❌ Ошибка загрузки:', error);
            this.showNotification('❌ Не удалось загрузить данные новеллы', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    renderSceneList() {
        const sceneList = document.getElementById('scene-list');
        if (!sceneList) return;
        
        sceneList.innerHTML = '';
        
        // Сортируем сцены по порядку
        this.scenes.sort((a, b) => (a.order || 0) - (b.order || 0));
        
        this.scenes.forEach((scene, index) => {
            const sceneElement = document.createElement('div');
            sceneElement.className = `scene-item-advanced ${index === this.currentSceneIndex ? 'active' : ''}`;
            
            const sceneName = scene.name || `Сцена ${index + 1}`;
            const previewText = scene.text ? 
                (scene.text.length > 50 ? scene.text.substring(0, 50) + '...' : scene.text) :
                '<em>Нет текста</em>';
            
            const spriteCount = Array.isArray(scene.sprites) ? scene.sprites.length : 0;
            
            sceneElement.innerHTML = `
                <div class="scene-item-header">
                    <span class="scene-number">${NovelBuilder.escapeHtml(sceneName)}</span>
                    <button onclick="novelBuilder.deleteScene(${index})" 
                            class="btn btn-sm btn-danger" style="padding: 2px 6px;">
                        ✕
                    </button>
                </div>
                <input type="text" class="scene-name-input" 
                       value="${NovelBuilder.escapeHtml(sceneName)}"
                       placeholder="Название сцены..."
                       onchange="novelBuilder.updateSceneName(${index}, this.value)"
                       onclick="event.stopPropagation()">
                <div class="scene-preview-text">
                    ${NovelBuilder.escapeHtml(previewText)}
                </div>
                ${spriteCount > 0 ? `<small style="color: #666;">Спрайтов: ${spriteCount}</small>` : ''}
            `;
            
            sceneElement.addEventListener('click', () => this.selectScene(index));
            sceneList.appendChild(sceneElement);
        });
    }
    
    selectScene(index) {
        if (index < 0 || index >= this.scenes.length) return;
        
        console.log(`🎬 Выбрана сцена ${index}:`, this.scenes[index]);
        
        // Снимаем выделение со всех сцен
        document.querySelectorAll('.scene-item-advanced').forEach(item => {
            item.classList.remove('active');
        });
        
        // Выделяем выбранную сцену
        const sceneItems = document.querySelectorAll('.scene-item-advanced');
        if (sceneItems[index]) {
            sceneItems[index].classList.add('active');
        }
        
        this.currentSceneIndex = index;
        const scene = this.scenes[index];
        
        // Заполняем форму редактора
        document.getElementById('scene-name').value = scene.name || `Сцена ${index + 1}`;
        document.getElementById('scene-text').value = scene.text || '';
        
        // Устанавливаем фон
        const backgroundDiv = document.getElementById('canvas-background');
        if (scene.background) {
            backgroundDiv.innerHTML = `
                <img src="${scene.background}" alt="Фон" 
                     style="width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0;">
            `;
            document.getElementById('background-preview').innerHTML = `
                <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                    <strong>Текущий фон:</strong><br>
                    <img src="${scene.background}" style="max-width: 100%; max-height: 100px; margin-top: 5px; border-radius: 4px;">
                </div>
            `;
        } else {
            backgroundDiv.innerHTML = '';
            document.getElementById('background-preview').innerHTML = '';
        }
        
        // Загружаем спрайты
        this.currentSprites = Array.isArray(scene.sprites) ? [...scene.sprites] : [];
        this.renderCanvasSprites();
        this.renderSpritesList();
        
        // Загружаем варианты выбора
        this.choices = Array.isArray(scene.choices) ? scene.choices : [];
        this.renderChoicesList();
        
        console.log(`✅ Сцена ${index} загружена`);
    }
    
    renderCanvasSprites() {
    const container = document.getElementById('sprites-container');
    if (!container) return;

    container.innerHTML = '';

    const canvasSprites = this.currentSprites.filter(s => s.isOnCanvas);
    canvasSprites.sort((a, b) => a.zIndex - b.zIndex);

    canvasSprites.forEach(sprite => {
        const spriteElement = document.createElement('div');
        spriteElement.className = 'sprite-item';
        spriteElement.id = 'sprite-' + sprite.id;

        spriteElement.style.cssText = `
            position: absolute;
            left: ${sprite.x}px;
            top: ${sprite.y}px;
            width: ${sprite.width}px;
            height: ${sprite.height}px;
            transform: rotate(${sprite.rotation}deg);
            z-index: ${sprite.zIndex};
            cursor: ${this.activeTool === 'move'
                ? 'move'
                : this.activeTool === 'delete'
                ? 'not-allowed'
                : 'default'};
        `;

        spriteElement.innerHTML = `
            <img src="${sprite.url}" alt="${sprite.name}"
                 class="sprite-image"
                 style="width: 100%; height: 100%; object-fit: contain; pointer-events: none;">
            <div class="sprite-label">${sprite.name}</div>
        `;

        // Drag & Drop (HTML5)
        spriteElement.draggable = this.activeTool === 'move';
        spriteElement.addEventListener('dragstart', (e) => {
            if (this.activeTool !== 'move') return;
            e.dataTransfer.setData('sprite/canvas-id', sprite.id);
            this.draggingSprite = sprite;
        });

        // Перемещение мышью
        if (this.activeTool === 'move') {
            this.makeDraggable(spriteElement, sprite);
        }

        // ===== УДАЛЕНИЕ СПРАЙТА =====
        spriteElement.addEventListener('click', (e) => {
            if (this.activeTool !== 'delete') return;

            e.stopPropagation();
            e.preventDefault();

            if (!confirm(`Удалить спрайт "${sprite.name}"?`)) return;

            // Удаляем из всех спрайтов
            this.currentSprites = this.currentSprites.filter(s => s.id !== sprite.id);

            // Обновляем сцену
            if (this.currentSceneIndex !== -1) {
                this.scenes[this.currentSceneIndex].sprites =
                    this.currentSprites.filter(s => s.isOnCanvas);
            }

            this.renderCanvasSprites();
            this.renderSpritesList();

            this.showNotification(`🗑️ Спрайт "${sprite.name}" удалён`, 'info');
        });

        container.appendChild(spriteElement);
    });

    // Подсказка на пустом холсте
    const hint = document.getElementById('canvas-hint');
    if (hint) {
        hint.style.display = canvasSprites.length === 0 ? 'block' : 'none';
    }
}
    
    renderSpritesList() {
        const spritesList = document.getElementById('sprites-list');
        if (!spritesList) return;
        
        spritesList.innerHTML = '';
        
        const availableSprites = this.currentSprites.filter(s => !s.isOnCanvas);
        
        if (availableSprites.length === 0) {
            spritesList.innerHTML = `
                <div class="empty-choices">
                    <p>Нет доступных спрайтов</p>
                    <p>Загрузите изображения персонажей</p>
                </div>
            `;
            return;
        }
        
        availableSprites.forEach(sprite => {
            const spriteElement = document.createElement('div');
            spriteElement.className = 'sprite-list-item';
            spriteElement.draggable = true;
            spriteElement.id = 'sprite-item-' + sprite.id;
            
            spriteElement.innerHTML = `
                <img src="${sprite.url}" alt="${sprite.name}" class="sprite-thumbnail">
                <div class="sprite-list-info">
                    <div class="sprite-list-name">${sprite.name}</div>
                    <small style="color: #666;">Перетащите на сцену</small>
                </div>
            `;
            
            spriteElement.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('sprite/id', sprite.id);
                e.dataTransfer.setData('sprite/name', sprite.name);
                e.dataTransfer.setData('sprite/url', sprite.url);
            });
            
            spritesList.appendChild(spriteElement);
        });
    }
    
    renderChoicesList() {
        const choicesList = document.getElementById('choices-list');
        if (!choicesList) return;
        
        choicesList.innerHTML = '';
        
        if (this.choices.length === 0) {
            choicesList.innerHTML = `
                <div class="empty-choices">
                    <p>Пока нет вариантов выбора.</p>
                    <p>Читатель увидит только кнопку "Далее".</p>
                </div>
            `;
            return;
        }
        
        this.choices.forEach((choice, index) => {
            const choiceElement = document.createElement('div');
            choiceElement.className = 'choice-item';
            
            let sceneOptions = '';
            this.scenes.forEach((scene, sceneIndex) => {
                const sceneNum = sceneIndex + 1;
                sceneOptions += `<option value="${sceneNum}" ${choice.nextScene === sceneNum ? 'selected' : ''}>
                    Сцена ${sceneNum}: ${scene.name || 'Без названия'}
                </option>`;
            });
            
            choiceElement.innerHTML = `
                <div class="choice-header">
                    <strong>Вариант ${index + 1}</strong>
                    <div class="choice-actions">
                        <button onclick="novelBuilder.moveChoiceUp(${index})" class="btn btn-sm btn-secondary" ${index === 0 ? 'disabled' : ''}>
                            ↑
                        </button>
                        <button onclick="novelBuilder.moveChoiceDown(${index})" class="btn btn-sm btn-secondary" ${index === this.choices.length - 1 ? 'disabled' : ''}>
                            ↓
                        </button>
                        <button onclick="novelBuilder.deleteChoice(${index})" class="btn btn-sm btn-danger">
                            ✕
                        </button>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Текст варианта:</label>
                    <input type="text" class="form-control choice-text" 
                           value="${NovelBuilder.escapeHtml(choice.text || '')}" 
                           placeholder="Что выберет читатель?"
                           oninput="novelBuilder.updateChoiceText(${index}, this.value)">
                </div>
                <div class="form-group">
                    <label class="form-label">Ведет на сцену:</label>
                    <select class="form-control choice-next-scene" 
                            onchange="novelBuilder.updateChoiceNextScene(${index}, this.value)">
                        ${sceneOptions}
                        <option value="0" ${choice.nextScene === 0 ? 'selected' : ''}>Конец истории</option>
                    </select>
                </div>
            `;
            
            choicesList.appendChild(choiceElement);
        });
    }
    
    addNewScene() {
        const newScene = {
            id: 'scene_' + Date.now(),
            name: `Сцена ${this.scenes.length + 1}`,
            text: '',
            background: '',
            order: this.scenes.length,
            choices: [],
            sprites: []
        };
        
        this.scenes.push(newScene);
        this.renderSceneList();
        this.selectScene(this.scenes.length - 1);
        
        // Фокус на поле названия
        setTimeout(() => {
            document.getElementById('scene-name').focus();
        }, 100);
        
        this.showNotification('✅ Новая сцена добавлена', 'success');
    }
    
    updateSceneName(index, name) {
        if (this.scenes[index]) {
            this.scenes[index].name = name;
            this.renderSceneList();
        }
    }
    
    saveCurrentScene() {
        if (this.currentSceneIndex === -1) {
            this.showNotification('⚠️ Сначала выберите или создайте сцену', 'info');
            return;
        }
        
        const scene = this.scenes[this.currentSceneIndex];
        scene.name = document.getElementById('scene-name').value;
        scene.text = document.getElementById('scene-text').value;
        scene.choices = [...this.choices];
        scene.sprites = this.currentSprites.filter(s => s.isOnCanvas);
        
        console.log(`💾 Сохранение сцены ${this.currentSceneIndex}:`, {
            name: scene.name,
            textLength: scene.text.length,
            choices: scene.choices.length,
            sprites: scene.sprites.length
        });
        
        // Обновляем отображение в списке
        this.renderSceneList();
        
        this.showNotification('✅ Сцена сохранена!', 'success');
    }
    
    async saveNovel() {
        try {
            console.log("💾 Начинаю сохранение новеллы...");
            
            // Сначала сохраняем текущую сцену
            this.saveCurrentScene();
            
            const saveBtn = document.getElementById('save-btn');
            const originalText = saveBtn.innerHTML;
            saveBtn.disabled = true;
            saveBtn.innerHTML = '⏳ Сохранение...';
            
            const novelData = {
                title: document.getElementById('novel-title').value,
                description: document.getElementById('novel-description').value,
                is_published: document.getElementById('novel-published').checked,
                scenes: this.scenes.map(scene => ({
                    ...scene,
                    choices: Array.isArray(scene.choices) ? scene.choices : [],
                    sprites: Array.isArray(scene.sprites) ? scene.sprites : []
                }))
            };
            
            console.log("📤 Отправляю данные для сохранения:", {
                title: novelData.title,
                scenes: novelData.scenes.length,
                scene1: novelData.scenes[0] ? {
                    name: novelData.scenes[0].name,
                    textLength: novelData.scenes[0].text.length,
                    choices: novelData.scenes[0].choices.length,
                    sprites: novelData.scenes[0].sprites.length
                } : null
            });
            
            const response = await fetch(`/api/save_novel/${this.novelId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(novelData)
            });
            
            const data = await response.json();
            
            console.log("📥 Ответ от сервера:", data);
            
            if (data.success) {
                this.showNotification('✅ Новелла сохранена!', 'success');
                this.updateNovelTitle(novelData.title);
                this.updatePublishStatus(novelData.is_published);
                
                // Обновляем кнопку публикации
                const publishBtn = document.getElementById('publish-btn');
                publishBtn.innerHTML = novelData.is_published ? '✅ Опубликовано' : '📢 Опубликовать';
                
            } else {
                this.showNotification('❌ Ошибка: ' + data.error, 'error');
            }
            
        } catch (error) {
            console.error('❌ Ошибка сохранения:', error);
            this.showNotification('❌ Ошибка сети при сохранении', 'error');
        } finally {
            const saveBtn = document.getElementById('save-btn');
            saveBtn.disabled = false;
            saveBtn.innerHTML = '💾 Сохранить';
        }
    }
    
    async publishNovel() {
        try {
            // Сначала сохраняем
            await this.saveNovel();
            
            const response = await fetch(`/api/publish_novel/${this.novelId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('🎉 Новелла опубликована!', 'success');
                this.updatePublishStatus(true);
                document.getElementById('novel-published').checked = true;
                
                const publishBtn = document.getElementById('publish-btn');
                publishBtn.innerHTML = '✅ Опубликовано';
                publishBtn.disabled = true;
                
            } else {
                this.showNotification('❌ Ошибка публикации: ' + data.error, 'error');
            }
            
        } catch (error) {
            console.error('Ошибка публикации:', error);
            this.showNotification('❌ Ошибка сети при публикации', 'error');
        }
    }
    
    previewNovel() {
        if (this.novelId) {
            // Сохраняем перед предпросмотром
            this.saveNovel().then(() => {
                // Открываем предпросмотр в новой вкладке
                window.open(`/view/${this.novelId}`, '_blank');
            }).catch(error => {
                this.showNotification('❌ Ошибка при сохранении перед предпросмотром', 'error');
            });
        } else {
            this.showNotification('❌ Сначала сохраните новеллу', 'error');
        }
    }
    
    // ========== ОБРАБОТКА ФАЙЛОВ ==========
    
    handleBackgroundFile(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        if (!file.type.startsWith('image/')) {
            this.showNotification('❌ Пожалуйста, выберите изображение', 'error');
            return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('❌ Файл слишком большой (макс. 5MB)', 'error');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const backgroundUrl = e.target.result;
            
            // Обновляем фон на холсте
            const backgroundDiv = document.getElementById('canvas-background');
            backgroundDiv.innerHTML = `
                <img src="${backgroundUrl}" alt="Фон" 
                     style="width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0;">
            `;
            
            // Обновляем данные сцены
            if (this.currentSceneIndex !== -1) {
                this.scenes[this.currentSceneIndex].background = backgroundUrl;
            }
            
            // Показываем превью
            document.getElementById('background-preview').innerHTML = `
                <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                    <strong>Загруженный фон:</strong><br>
                    <img src="${backgroundUrl}" style="max-width: 100%; max-height: 100px; margin-top: 5px; border-radius: 4px;">
                </div>
            `;
            
            this.showNotification('✅ Фон загружен успешно', 'success');
        };
        reader.readAsDataURL(file);
    }
    
    handleSpriteFiles(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (!file.type.startsWith('image/')) continue;
            
            if (file.size > 3 * 1024 * 1024) {
                this.showNotification(`❌ Файл "${file.name}" слишком большой`, 'error');
                continue;
            }
            
            const reader = new FileReader();
            reader.onload = (e) => {
                const spriteUrl = e.target.result;
                
                // Добавляем в список доступных спрайтов
                const sprite = {
                    id: 'sprite_' + Date.now() + '_' + i,
                    url: spriteUrl,
                    name: file.name.replace(/\.[^/.]+$/, ""),
                    isOnCanvas: false
                };
                
                this.currentSprites.push(sprite);
                this.renderSpritesList();
                this.showNotification(`✅ Спрайт "${sprite.name}" добавлен`, 'success');
            };
            reader.readAsDataURL(file);
        }
    }
    
    handleBackgroundDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleBackgroundFile(files);
        }
    }
    
    handleSpriteDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleSpriteFiles(files);
        }
    }
    
    dropOnCanvas(e) {
        e.preventDefault();
        const spriteId = e.dataTransfer.getData('sprite/id');
        const spriteUrl = e.dataTransfer.getData('sprite/url');
        const spriteName = e.dataTransfer.getData('sprite/name');
        
        if (spriteId && spriteUrl) {
            const rect = e.currentTarget.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            this.addSpriteToCanvas(spriteUrl, spriteName, x, y);
        }
    }
    
    addSpriteToCanvas(url, name, x, y) {
        const spriteId = 'sprite_instance_' + Date.now();
        const sprite = {
            id: spriteId,
            url: url,
            name: name,
            x: x - 75,
            y: y - 100,
            width: 150,
            height: 200,
            rotation: 0,
            zIndex: this.currentSprites.filter(s => s.isOnCanvas).length,
            isOnCanvas: true
        };
        
        this.currentSprites.push(sprite);
        this.renderCanvasSprites();
        
        // Обновляем данные сцены
        if (this.currentSceneIndex !== -1) {
            this.scenes[this.currentSceneIndex].sprites = this.currentSprites.filter(s => s.isOnCanvas);
        }
        
        this.showNotification(`✅ Спрайт "${name}" добавлен на сцену`, 'success');
    }
    
    // ========== УПРАВЛЕНИЕ СПРАЙТАМИ ==========
    
    makeDraggable(element, sprite) {
        let isDragging = false;
        let offsetX, offsetY;
        
        element.addEventListener('mousedown', (e) => {
            if (this.activeTool !== 'move') return;
            
            isDragging = true;
            offsetX = e.clientX - sprite.x;
            offsetY = e.clientY - sprite.y;
            
            const mouseMoveHandler = (e) => {
                if (!isDragging) return;
                
                sprite.x = e.clientX - offsetX;
                sprite.y = e.clientY - offsetY;
                
                element.style.left = sprite.x + 'px';
                element.style.top = sprite.y + 'px';
            };
            
            const mouseUpHandler = () => {
                isDragging = false;
                document.removeEventListener('mousemove', mouseMoveHandler);
                document.removeEventListener('mouseup', mouseUpHandler);
                
                // Обновляем данные сцены
                if (this.currentSceneIndex !== -1) {
                    this.scenes[this.currentSceneIndex].sprites = this.currentSprites.filter(s => s.isOnCanvas);
                }
            };
            
            document.addEventListener('mousemove', mouseMoveHandler);
            document.addEventListener('mouseup', mouseUpHandler);
            
            e.preventDefault();
        });
    }
    
    selectTool(tool) {
        this.activeTool = tool;
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        this.renderCanvasSprites();
    }
    
    // ========== УПРАВЛЕНИЕ ВЫБОРАМИ ==========
    
    addNewChoice() {
        if (this.currentSceneIndex === -1) {
            this.showNotification('⚠️ Сначала выберите или создайте сцену', 'info');
            return;
        }
        
        const newChoice = {
            id: 'choice_' + Date.now(),
            text: '',
            nextScene: this.scenes.length > 1 ? 2 : 1
        };
        
        this.choices.push(newChoice);
        this.renderChoicesList();
    }
    
    updateChoiceText(index, text) {
        if (this.choices[index]) {
            this.choices[index].text = text;
        }
    }
    
    updateChoiceNextScene(index, nextScene) {
        if (this.choices[index]) {
            this.choices[index].nextScene = parseInt(nextScene);
        }
    }
    
    moveChoiceUp(index) {
        if (index > 0) {
            [this.choices[index], this.choices[index - 1]] = [this.choices[index - 1], this.choices[index]];
            this.renderChoicesList();
        }
    }
    
    moveChoiceDown(index) {
        if (index < this.choices.length - 1) {
            [this.choices[index], this.choices[index + 1]] = [this.choices[index + 1], this.choices[index]];
            this.renderChoicesList();
        }
    }
    
    deleteChoice(index) {
        if (confirm('Удалить этот вариант выбора?')) {
            this.choices.splice(index, 1);
            this.renderChoicesList();
        }
    }
    
    deleteScene(index) {
        if (!confirm(`Удалить сцену ${index + 1}? Все варианты выбора и спрайты в этой сцене будут потеряны.`)) {
            return;
        }
        
        this.scenes.splice(index, 1);
        
        // Обновляем порядок сцен
        this.scenes.forEach((scene, i) => {
            scene.order = i;
        });
        
        // Обновляем ссылки в вариантах выбора
        this.scenes.forEach(scene => {
            if (scene.choices) {
                scene.choices.forEach(choice => {
                    if (choice.nextScene > index + 1) {
                        choice.nextScene--;
                    } else if (choice.nextScene === index + 1) {
                        choice.nextScene = 0;
                    }
                });
            }
        });
        
        // Выбираем другую сцену
        if (this.scenes.length > 0) {
            this.selectScene(Math.max(0, index - 1));
        } else {
            this.addNewScene();
        }
        
        this.renderSceneList();
        this.showNotification('🗑️ Сцена удалена', 'info');
    }
    
    // ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
    
    updateNovelTitle(title) {
        const titleElement = document.getElementById('novel-title-display');
        if (titleElement) {
            titleElement.textContent = title;
        }
    }
    
    updatePublishStatus(isPublished) {
        const badge = document.getElementById('publish-status-badge');
        if (badge) {
            badge.textContent = isPublished ? 'Опубликовано' : 'Черновик';
            badge.className = `status-badge ${isPublished ? 'status-published' : 'status-draft'}`;
        }
    }
    
    showNotification(message, type = 'info') {
        const notificationArea = document.getElementById('notification-area');
        if (!notificationArea) return;
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            z-index: 10000;
            animation: slideIn 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 400px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
                <span>${message}</span>
            </div>
        `;
        
        notificationArea.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    showLoading() {
        let loadingDiv = document.getElementById('loading-overlay');
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'loading-overlay';
            loadingDiv.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255,255,255,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;
            loadingDiv.innerHTML = `
                <div class="loading-spinner"></div>
            `;
            document.body.appendChild(loadingDiv);
        }
        loadingDiv.style.display = 'flex';
    }
    
    hideLoading() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }
    
    static escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const novelDataElement = document.getElementById('novel-data');
    if (novelDataElement) {
        const novelId = parseInt(novelDataElement.getAttribute('data-novel-id'));
        if (novelId && novelId > 0) {
            window.novelBuilder = new NovelBuilder(novelId);
        }
    }
    
    // Добавляем стили для анимаций если их нет
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
            .loading-spinner {
                border: 3px solid #f3f4f6;
                border-top: 3px solid #4f46e5;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
    }
});