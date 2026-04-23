

const API_URL = "/api-proxy/api";

let userSettings = JSON.parse(localStorage.getItem('userSettings')) || {
    displayName: "", theme: "System", aiPrefs: "", profilePhoto: ""
};

function applySettings() {
    if(userSettings.displayName) {
        const unEl = document.getElementById('userName');
        if(unEl) unEl.textContent = userSettings.displayName;
    }
    if(userSettings.theme === 'Dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }
    if(userSettings.profilePhoto) {
        const uA = document.getElementById('userAvatar');
        if(uA) uA.innerHTML = `<img src="${userSettings.profilePhoto}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
    }
}

function switchSettingsTab(tab, event) {
    document.querySelectorAll('.settings-tab').forEach(b => b.classList.remove('active'));
    if(event) event.target.classList.add('active');
    const area = document.getElementById('settingsContentArea');
    if (tab === 'profile') area.innerHTML = `<div id="tab-profile"><h3>Profile</h3><p style="color:#6b7280; font-size:13px; margin: 8px 0;">Manage your public display details.</p><label style="font-size:12px;">Profile Photo</label><input type="file" id="settingsPhotoInput" accept="image/*" style="display:block; margin:4px 0 12px;"><input type="text" id="settingsNameInput" placeholder="Display Name" style="width:100%; padding:8px; margin-top:8px; border:1px solid #d1d5db; border-radius:6px;" value="${userSettings.displayName||''}"><button style="margin-top:16px; background:#10a37f; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;" onclick="saveSettings()">Save</button></div>`;
    if (tab === 'theme') area.innerHTML = `<div><h3>Theme</h3><p style="font-size:13px; color:#6b7280; margin-top:8px;">Select light or dark mode.</p><select id="settingsThemeInput" style="margin-top:8px; padding:8px; width:100%; border-radius:6px;"><option ${userSettings.theme==='System'?'selected':''}>System</option><option ${userSettings.theme==='Light'?'selected':''}>Light</option><option ${userSettings.theme==='Dark'?'selected':''}>Dark</option></select><button style="margin-top:16px; background:#10a37f; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;" onclick="saveSettings()">Save</button></div>`;
    if (tab === 'ai') area.innerHTML = `<div><h3>AI Prefs</h3><p style="font-size:13px; color:#6b7280; margin-top:8px;">Custom AI System Prompts.</p><textarea style="margin-top:8px; padding:8px; width:100%; border-radius:6px; height: 80px;" placeholder="E.g., You are a strict coder."></textarea></div>`;
    if (tab === 'account') area.innerHTML = `<div><h3>Account</h3><p style="font-size:13px; color:#6b7280; margin-top:8px;">Delete or export data.</p><button style="margin-top:8px; color:#ef4444; background:#fee; border:none; padding:8px; border-radius:6px; cursor:pointer; width:100%;">Delete Account</button></div>`;
}

function saveSettings() {
    const nameInput = document.getElementById('settingsNameInput');
    const themeInput = document.getElementById('settingsThemeInput');
    const photoInput = document.getElementById('settingsPhotoInput');
    
    if(nameInput) userSettings.displayName = nameInput.value;
    if(themeInput) userSettings.theme = themeInput.value;
    
    if(photoInput && photoInput.files && photoInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(evt) {
            userSettings.profilePhoto = evt.target.result;
            localStorage.setItem('userSettings', JSON.stringify(userSettings));
            applySettings();
        };
        reader.readAsDataURL(photoInput.files[0]);
    } else {
        localStorage.setItem('userSettings', JSON.stringify(userSettings));
        applySettings();
    }

    document.getElementById('settingsModal').classList.remove('open');
    alert("Settings Saved!");
}

document.addEventListener("mouseup", (e) => {
    let selectedText = window.getSelection().toString().trim();
    let toolbar = document.getElementById('selectionToolbar');
    if (selectedText.length > 0 && e.target.closest('.message-content')) {
        toolbar.style.display = 'flex';
        toolbar.style.left = `${e.pageX}px`;
        toolbar.style.top = `${e.pageY - 40}px`;
        toolbar.style.pointerEvents = 'auto';
        toolbar.style.opacity = '1';
    } else if (!e.target.closest('#selectionToolbar')) {
        toolbar.style.pointerEvents = 'none';
        toolbar.style.opacity = '0';
        setTimeout(() => toolbar.style.display = 'none', 200);
    }
});

function askAiSelected() {
    const text = window.getSelection().toString().trim();
    if (text) {
        document.getElementById("messageInput").value = "Explain this: " + text;
        updateSendButton();
    }
    document.getElementById("selectionToolbar").style.opacity = '0';
}

function shareSelected() {
    const text = window.getSelection().toString().trim();
    if (text) navigator.clipboard.writeText(text);
    document.getElementById("selectionToolbar").style.opacity = '0';
    alert("Copied to clipboard!");
}

let currentChatId = null;
let chats = [];

/* ================= AUTH ================= */

function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_email");
    window.location.href = "login.html";
}

async function getAccessToken() {
    return localStorage.getItem("access_token");
}

/* ================= INITIAL LOAD ================= */

window.addEventListener("load", async () => {

    const token = await getAccessToken();

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const email = localStorage.getItem("user_email") || "User";
    const username = email.includes('@') ? email.split('@')[0] : email;

    document.getElementById("userName").textContent = username;
    document.getElementById("userAvatar").textContent =
        email[0].toUpperCase();

    applySettings();
    await loadChats();
});


/* ================= CHAT LIST ================= */

async function loadChats() {

    const token = await getAccessToken();

    if (!token) {
        console.log("No token found");
        return logout();
    }

    const res = await fetch(`${API_URL}/chats`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!res.ok) {

        console.error("API ERROR:", res.status);

        const txt = await res.text();
        console.error(txt);

        return;
    }

    const data = await res.json();

    chats = data.chats || [];

    renderChatList();

    if (chats.length > 0) {
        selectChat(chats[0].id);
    } else {
        await createNewChat();
    }
}


function renderChatList() {

    const sidebar = document.getElementById("chatList");
    sidebar.innerHTML = "";

    chats.forEach(chat => {

        const btn = document.createElement("div");

        btn.className = "chat-item";
        btn.textContent = chat.title || "Untitled Chat";

        btn.onclick = () => selectChat(chat.id);

        if (chat.id === currentChatId)
            btn.classList.add("active");

        sidebar.appendChild(btn);
    });
}


/* ================= SEARCH HIGHLIGHTING ================= */
let searchMatches = [];
let currentMatchIndex = -1;

function applySearchHighlight(html, query) {
    if (!query) return html;
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    // Match the query only outside HTML tags
    const regex = new RegExp(`(?![^<]+>)(${escapedQuery})`, "gi");
    return html.replace(regex, '<mark class="search-match">$1</mark>');
}

function initSearchNav() {
    const nav = document.getElementById("inChatSearchNav");
    if (!activeSearchQuery) {
        nav.style.display = "none";
        return;
    }
    nav.style.display = "flex";
    searchMatches = Array.from(document.querySelectorAll(".search-match"));
    currentMatchIndex = searchMatches.length > 0 ? 0 : -1;
    updateSearchNavUI();
    if (currentMatchIndex >= 0) {
        focusSearchMatch(currentMatchIndex);
    }
}

function updateSearchNavUI() {
    const counter = document.getElementById("searchNavCounter");
    if (searchMatches.length === 0) {
        counter.textContent = "0 / 0";
    } else {
        counter.textContent = `${currentMatchIndex + 1} / ${searchMatches.length}`;
    }
}

function focusSearchMatch(index) {
    searchMatches.forEach(m => m.classList.remove("active"));
    if (index >= 0 && index < searchMatches.length) {
        const el = searchMatches[index];
        el.classList.add("active");
        el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    updateSearchNavUI();
}

document.getElementById("searchNavPrev").addEventListener("click", () => {
    if (searchMatches.length === 0) return;
    currentMatchIndex = (currentMatchIndex - 1 + searchMatches.length) % searchMatches.length;
    focusSearchMatch(currentMatchIndex);
});

document.getElementById("searchNavNext").addEventListener("click", () => {
    if (searchMatches.length === 0) return;
    currentMatchIndex = (currentMatchIndex + 1) % searchMatches.length;
    focusSearchMatch(currentMatchIndex);
});

document.getElementById("searchNavClose").addEventListener("click", () => {
    document.getElementById("inChatSearchNav").style.display = "none";
    activeSearchQuery = "";
    searchMatches.forEach(m => {
        const parent = m.parentNode;
        parent.replaceChild(document.createTextNode(m.textContent), m);
        parent.normalize();
    });
    searchMatches = [];
});

/* ================= SELECT CHAT ================= */

async function selectChat(chatId) {

    currentChatId = chatId;

    renderChatList();

    await loadMessages(chatId);
    initSearchNav();
}


async function loadMessages(chatId) {

    const token = await getAccessToken();
    if (!token) return logout();

    const res = await fetch(`${API_URL}/chats/${chatId}/messages`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        console.error("Failed loading messages");
        return;
    }

    const data = await res.json();

    const chatMessages =
        document.getElementById("chatMessages");

    chatMessages.classList.remove("empty");
    chatMessages.innerHTML = "";

    data.forEach(msg => {
        addMessageToUI(msg.role, msg.content);
    });
}


/* ================= SEND MESSAGE ================= */

async function sendMessage() {
    const input = document.getElementById("messageInput");
    let message = input.value.trim();

    if (!message && !attachedFile && !attachedImageBase64) return;
    if (!currentChatId) return alert("Create or select a chat first.");

    // Generate attachment bubble UI inside user message if attached
    let displayHtml = `<p>${escapeHtml(message)}</p>`;
    if (attachedFile || attachedImageBase64) {
        let previewHtml = "";
        if (attachedImageBase64) {
            previewHtml = `<img src="${attachedImageBase64}" style="max-height:100px; border-radius:8px; margin-bottom:8px; display:block;">`;
        } else if (attachedFile) {
            previewHtml = `<div style="background:rgba(0,0,0,0.05); padding:8px 12px; border-radius:8px; margin-bottom:8px; display:inline-flex; align-items:center; gap:8px; font-size:12px;"><svg width="16" height="16" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>${escapeHtml(attachedFile.name)}</div>`;
        }
        displayHtml = previewHtml + displayHtml;
    }

    addMessageToUI("user", displayHtml, false, null, true); // pass true for isRawHtml
    
    input.value = "";
    
    // Build payload
    const payload = new FormData();
    payload.append("message", message);
    if (attachedFile) {
        payload.append("file", attachedFile);
    }

    // Reset attachments
    attachedFile = null;
    attachedImageBase64 = null;
    const preview = document.getElementById("attachmentPreview");
    if (preview) preview.style.display = "none";
    const fileInput = document.getElementById("chatAttachmentInput");
    if (fileInput) fileInput.value = "";
    
    updateSendButton();

    const token = await getAccessToken();
    if (!token) return logout();

    const loadingId = "msg-" + Date.now();
    // Add empty message container for streaming
    addMessageToUI("assistant", "", false, loadingId);
    const msgDiv = document.getElementById(loadingId);
    const contentDiv = msgDiv.querySelector('.message-content');
    contentDiv.innerHTML = `<span class="typing-indicator"><span></span><span></span><span></span></span>`;

    try {
        const res = await fetch(`${API_URL}/chats/${currentChatId}/message`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            },
            body: payload
        });

        if (!res.ok) {
            contentDiv.innerHTML = "Sorry, an error occurred.";
            return;
        }

        contentDiv.innerHTML = ""; // Clear loader
        let accumulatedText = "";
        
        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let done = false;
        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            if (value) {
                const chunkStr = decoder.decode(value, { stream: true });
                const lines = chunkStr.split('\n');
                
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const data = JSON.parse(line.substring(6));
                            if (data.type === "title") {
                                const chatObj = chats.find(c => c.id === currentChatId);
                                if (chatObj && chatObj.title !== data.title) {
                                    chatObj.title = data.title;
                                    renderChatList();
                                }
                            } else if (data.type === "chunk") {
                                accumulatedText += data.text;
                                let renderHtml = DOMPurify.sanitize(marked.parse(accumulatedText));
                                if (activeSearchQuery) {
                                    renderHtml = applySearchHighlight(renderHtml, activeSearchQuery);
                                }
                                contentDiv.innerHTML = renderHtml;
                                
                                // Auto scroll logic: only scroll if user is near bottom
                                const chatContainer = document.getElementById("chatMessages");
                                const isScrolledToBottom = chatContainer.scrollHeight - chatContainer.clientHeight <= chatContainer.scrollTop + 50;
                                if (isScrolledToBottom) {
                                    chatContainer.scrollTop = chatContainer.scrollHeight;
                                }
                            }
                        } catch (e) {
                            console.error("Error parsing SSE JSON:", e);
                        }
                    }
                }
            }
        }
        
        let finalRenderHtml = DOMPurify.sanitize(marked.parse(accumulatedText));
        if (activeSearchQuery) {
            finalRenderHtml = applySearchHighlight(finalRenderHtml, activeSearchQuery);
        }
        contentDiv.innerHTML = finalRenderHtml;
        
        // Re-init search navigation to pick up newly added marks during stream
        if (activeSearchQuery) {
            initSearchNav();
        }
        
        // Trigger TTS if not empty
        if (accumulatedText.trim()) {
            const utterance = new SpeechSynthesisUtterance(accumulatedText);
            utterance.lang = 'en-US';
            utterance.rate = 1.05;
            window.speechSynthesis.speak(utterance);
        }

    } catch (e) {
        console.error(e);
        if(contentDiv) contentDiv.innerHTML = "Sorry, an error occurred.";
    }
}


/* ================= CREATE NEW CHAT ================= */

async function createNewChat() {

    const token = await getAccessToken();

    if (!token) return logout();

    const res = await fetch(`${API_URL}/chats`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    });

    if (!res.ok) {
        console.error("Create chat failed");
        return;
    }

    const data = await res.json();

    chats.unshift(data.chat);

    renderChatList();

    selectChat(data.chat.id);
}


/* ================= UI ================= */

marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
  langPrefix: 'hljs language-'
});

function addMessageToUI(role, content, isNew = false, id = null, isRawHtml = false) {
    const chatMessages = document.getElementById("chatMessages");

    if (chatMessages.classList.contains("empty")) {
        chatMessages.classList.remove("empty");
        chatMessages.innerHTML = "";
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}`;
    if (id) messageDiv.id = id;

    const avatarHtml = role === "user" 
        ? (localStorage.getItem("user_email") || "U")[0].toUpperCase() 
        : "<img src='myLogo.png' class='ai-avatar-img'>";

    let contentHtml = "";
    if (role === "assistant") {
        contentHtml = DOMPurify.sanitize(marked.parse(content));
    } else {
        if (isRawHtml) {
            contentHtml = content; // already escaped when calling
        } else {
            contentHtml = `<p>${escapeHtml(content)}</p>`;
        }
    }
    
    if (activeSearchQuery) {
        contentHtml = applySearchHighlight(contentHtml, activeSearchQuery);
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarHtml}</div>
        <div class="message-content"></div>
    `;

    const contentDiv = messageDiv.querySelector('.message-content');
    chatMessages.appendChild(messageDiv);

    if (isNew && role === "assistant" && !id) {
        // Fallback for non-streaming assistant messages (though we stream now)
        contentDiv.innerHTML = "";
        let i = 0;
        const speed = 8;
        function typeWriter() {
            if (i < content.length) {
                i += speed;
                const currentText = content.substring(0, i);
                contentDiv.innerHTML = DOMPurify.sanitize(marked.parse(currentText));
                chatMessages.scrollTop = chatMessages.scrollHeight;
                requestAnimationFrame(typeWriter);
            } else {
                contentDiv.innerHTML = contentHtml;
                // Only scroll if it's the typewriter generating new text
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
        requestAnimationFrame(typeWriter);
    } else {
        contentDiv.innerHTML = contentHtml;
    }
}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


/* ================= INPUT ================= */

function autoResize(textarea) {

    textarea.style.height = "auto";

    textarea.style.height =
        textarea.scrollHeight + "px";
}

let attachedFile = null;
let attachedImageBase64 = null;

function updateSendButton() {
    const input = document.getElementById("messageInput");
    const button = document.getElementById("sendButton");

    if (input.value.trim().length > 0 || attachedImageBase64 || attachedFile) {
        button.disabled = false;
        button.classList.add("active");
    } else {
        button.disabled = true;
        button.classList.remove("active");
    }
}


/* ================= EVENTS ================= */

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector(".logout-btn").addEventListener("click", logout);
    document.getElementById("sendButton").addEventListener("click", sendMessage);
    document.querySelector(".new-chat-btn").addEventListener("click", createNewChat);

    const textarea = document.getElementById("messageInput");
    textarea.addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    textarea.addEventListener("input", () => {
        autoResize(textarea);
        updateSendButton();
    });

    const searchInput = document.getElementById("searchChatInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase();
            const items = document.querySelectorAll("#chatList .chat-item");
            items.forEach(item => {
                if (item.textContent.toLowerCase().includes(query)) {
                    item.style.display = "block";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }

    const chatAttachmentInput = document.getElementById("chatAttachmentInput");
    const attachmentPreview = document.getElementById("attachmentPreview");
    const attachmentImg = document.getElementById("attachmentImg");
    const removeAttachmentBtn = document.getElementById("removeAttachmentBtn");

    if (chatAttachmentInput) {
        chatAttachmentInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;
            attachedFile = file;
            if (file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = function(evt) {
                    attachedImageBase64 = evt.target.result;
                    attachmentImg.src = attachedImageBase64;
                    attachmentImg.style.display = "inline-block";
                    attachmentPreview.style.display = "block";
                    updateSendButton();
                };
                reader.readAsDataURL(file);
            } else {
                attachedImageBase64 = null;
                attachmentImg.style.display = "none"; 
                attachmentPreview.style.display = "block"; // just showing remove button for docs
                updateSendButton();
            }
        });
    }

    if (removeAttachmentBtn) {
        removeAttachmentBtn.addEventListener("click", () => {
            attachedFile = null;
            attachedImageBase64 = null;
            chatAttachmentInput.value = "";
            attachmentPreview.style.display = "none";
            updateSendButton();
        });
    }

    const attachBtn = document.getElementById("attachBtn");
    if (attachBtn) {
        attachBtn.addEventListener("click", () => {
            if (chatAttachmentInput) chatAttachmentInput.click();
        });
    }

    const shareBtn = document.getElementById("shareChatBtn");
    const toastContainer = document.getElementById("toastContainer");
    const toastMessage = document.getElementById("toastMessage");
    const toastCopyBtn = document.getElementById("toastCopyBtn");
    const toastCloseBtn = document.getElementById("toastCloseBtn");
    let toastTimeout;

    if (shareBtn) {
        shareBtn.addEventListener("click", () => {
            if (!currentChatId) {
                alert("Please select a chat to share.");
                return;
            }
            const link = window.location.origin + "/?chat=" + currentChatId;
            toastMessage.textContent = link;
            toastContainer.style.display = "flex";
            
            toastCopyBtn.onclick = () => {
                const tempInput = document.createElement("input");
                tempInput.value = link;
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand("copy");
                document.body.removeChild(tempInput);
                toastCopyBtn.textContent = "Copied!";
                setTimeout(() => { toastCopyBtn.textContent = "Copy"; }, 2000);
            };

            toastCloseBtn.onclick = () => {
                toastContainer.style.display = "none";
            };

            clearTimeout(toastTimeout);
            toastTimeout = setTimeout(() => {
                toastContainer.style.display = "none";
            }, 8000);
        });
    }

    const voiceBtn = document.getElementById("voiceBtn");
    let isDictating = false;
    let mediaRecorder = null;
    let audioContext = null;
    let silenceTimer = null;
    let audioChunks = [];
    const SILENCE_THRESHOLD = 2500; // 2.5 seconds
    const VOLUME_THRESHOLD = 5; // minimal volume threshold

    if (voiceBtn) {
        voiceBtn.addEventListener("click", async () => {
            if (isDictating) {
                // Manually turn off
                stopRecording();
            } else {
                // Turn on
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    startRecording(stream);
                } catch (err) {
                    alert("Microphone access denied or not supported.");
                    console.error("Mic error:", err);
                }
            }
        });
    }

    function startRecording(stream) {
        isDictating = true;
        voiceBtn.classList.add("recording-active");
        audioChunks = [];
        
        // Stop any ongoing TTS playback
        window.speechSynthesis.cancel();

        mediaRecorder = new MediaRecorder(stream);
        
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 512;
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        function detectSilence() {
            if (!isDictating) return;
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for(let i=0; i < dataArray.length; i++) sum += dataArray[i];
            let averageVolume = sum / dataArray.length;

            if (averageVolume < VOLUME_THRESHOLD) {
                if (!silenceTimer) {
                    silenceTimer = setTimeout(() => {
                        if (isDictating) {
                            console.log("Silence detected. Stopping and submitting...");
                            stopRecordingAndSubmit();
                        }
                    }, SILENCE_THRESHOLD);
                }
            } else {
                if (silenceTimer) {
                    clearTimeout(silenceTimer);
                    silenceTimer = null;
                }
            }
            requestAnimationFrame(detectSilence);
        }

        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) audioChunks.push(e.data);
        };

        mediaRecorder.start(250); // get chunks frequently
        detectSilence();
    }

    function stopRecording() {
        if (!isDictating) return;
        isDictating = false;
        voiceBtn.classList.remove("recording-active");
        if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; }
        if (mediaRecorder && mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
        if (audioContext) {
            audioContext.close();
        }
        // If manually stopped, we do NOT auto-submit.
    }

    function stopRecordingAndSubmit() {
        if (!isDictating) return;
        isDictating = false;
        voiceBtn.classList.remove("recording-active");
        if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null; }
        
        mediaRecorder.onstop = async () => {
            if (audioContext) audioContext.close();
            
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            
            // Send the audio blob to the backend as a standard file attachment
            attachedFile = new File([audioBlob], "voice_memo.webm", { type: mediaRecorder.mimeType });
            
            // Automatically submit the message
            document.getElementById("messageInput").value = "Transcribe and answer this voice note directly.";
            updateSendButton();
            await sendMessage();
        };
        
        if (mediaRecorder.state !== "inactive") {
            mediaRecorder.stop();
        }
    }

    // Wrap the original addMessageToUI to inject text-to-speech for assistant messages
    const originalAddMessageToUI = addMessageToUI;
    addMessageToUI = function(role, content, isNew = false, id = null, isRawHtml = false) {
        originalAddMessageToUI(role, content, isNew, id, isRawHtml);
        
        // If it's a completely new AI generation response (not loading/history)
        if (isNew && role === "assistant" && content && content.trim()) {
            const utterance = new SpeechSynthesisUtterance(content);
            utterance.lang = 'en-US';
            utterance.rate = 1.05; // slightly faster conversational tone
            window.speechSynthesis.speak(utterance);
        }
    };

    // =================================================
    // GLOBAL SEARCH (CTRL+K)
    // =================================================
    let activeSearchQuery = "";
    
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            const modal = document.getElementById("searchPalette");
            if (modal) {
                modal.classList.add("open");
                const input = document.getElementById("paletteSearchInput");
                if (input) {
                    input.value = "";
                    input.focus();
                    document.getElementById("paletteResults").innerHTML = '<div style="padding: 12px 16px; color: #6b7280; font-size: 14px; text-align: center;">Type to search all chats...</div>';
                }
            }
        }
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "o") {
            e.preventDefault();
            createNewChat();
        }
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "s") {
            e.preventDefault();
            const sidebar = document.querySelector(".sidebar");
            if (sidebar) sidebar.style.display = sidebar.style.display === "none" ? "flex" : "none";
        }
        if (e.shiftKey && e.key === "Escape") {
            e.preventDefault();
            const input = document.getElementById("messageInput");
            if (input) input.focus();
        }
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "u") {
            e.preventDefault();
            const fileInput = document.getElementById("chatAttachmentInput");
            if (fileInput) fileInput.click();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === "/") {
            e.preventDefault();
            const modal = document.getElementById("shortcutsModal");
            if (modal) modal.classList.toggle("open");
        }
    });

    const paletteSearchInput = document.getElementById("paletteSearchInput");
    let paletteTimeout = null;
    if (paletteSearchInput) {
        paletteSearchInput.addEventListener("input", (e) => {
            clearTimeout(paletteTimeout);
            const val = e.target.value.trim();
            const resContainer = document.getElementById("paletteResults");
            if (!val) {
                resContainer.innerHTML = '<div style="padding: 12px 16px; color: #6b7280; font-size: 14px; text-align: center;">Type to search all chats...</div>';
                return;
            }
            resContainer.innerHTML = '<div style="padding: 12px 16px; color: #6b7280; font-size: 14px; text-align: center;">Searching...</div>';
            
            paletteTimeout = setTimeout(async () => {
                const token = await getAccessToken();
                try {
                    const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(val)}`, {
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                    if (res.ok) {
                        const data = await res.json();
                        resContainer.innerHTML = "";
                        if (data.results.length === 0) {
                            resContainer.innerHTML = '<div style="padding: 12px 16px; color: #6b7280; font-size: 14px; text-align: center;">No matches found.</div>';
                        } else {
                            data.results.forEach(item => {
                                const div = document.createElement("div");
                                div.style.padding = "12px 16px";
                                div.style.borderBottom = "1px solid var(--border-color)";
                                div.style.cursor = "pointer";
                                div.innerHTML = `<div style="font-weight: 600;">${escapeHtml(item.title)}</div><div style="font-size: 12px; color: #6b7280;">${item.hits} matches</div>`;
                                div.onclick = () => {
                                    document.getElementById('searchPalette').classList.remove('open');
                                    activeSearchQuery = val;
                                    selectChat(item.chat_id);
                                };
                                div.onmouseover = () => div.style.background = "var(--input-bg)";
                                div.onmouseout = () => div.style.background = "transparent";
                                resContainer.appendChild(div);
                            });
                        }
                    }
                } catch (err) {
                    console.error(err);
                    resContainer.innerHTML = '<div style="padding: 12px 16px; color: #ef4444; font-size: 14px; text-align: center;">Error searching.</div>';
                }
            }, 300);
        });
    }

    // =================================================
    // LIVE VOICE CHAT (FULL DUPLEX)
    // =================================================
    const liveVoiceBtn = document.getElementById("liveVoiceBtn");
    let liveSocket = null;
    let liveAudioCtx = null;
    let liveMicStream = null;
    let liveProcessor = null;
    let nextPlayTime = 0;

    if (liveVoiceBtn) {
        liveVoiceBtn.addEventListener("click", toggleLiveVoice);
    }

    async function toggleLiveVoice() {
        if (liveSocket && liveSocket.readyState === WebSocket.OPEN) {
            stopLiveVoice();
        } else {
            await startLiveVoice();
        }
    }

    async function startLiveVoice() {
        try {
            liveVoiceBtn.style.color = "#ef4444"; // Red
            liveVoiceBtn.classList.add("active");
            
            const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            const token = localStorage.getItem("token");
            liveSocket = new WebSocket(`${protocol}//${window.location.host}/api/live-voice?token=${token}`);
            liveSocket.binaryType = "arraybuffer";

            liveSocket.onopen = async () => {
                console.log("[Live Voice] Connected to server.");
                await startMicrophone();
            };

            liveSocket.onmessage = async (event) => {
                if (typeof event.data === "string") {
                    const msg = JSON.parse(event.data);
                    if (msg.type === "audio") {
                        playAudioBase64(msg.data);
                    } else if (msg.type === "turnComplete") {
                        console.log("[Live Voice] Turn Complete");
                    }
                }
            };

            liveSocket.onclose = () => {
                stopLiveVoice();
            };

        } catch (e) {
            console.error("[Live Voice] Start failed:", e);
            stopLiveVoice();
        }
    }

    async function startMicrophone() {
        liveAudioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        nextPlayTime = liveAudioCtx.currentTime;
        
        liveMicStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
        const source = liveAudioCtx.createMediaStreamSource(liveMicStream);
        
        liveProcessor = liveAudioCtx.createScriptProcessor(4096, 1, 1);
        source.connect(liveProcessor);
        liveProcessor.connect(liveAudioCtx.destination);
        
        liveProcessor.onaudioprocess = (e) => {
            if (!liveSocket || liveSocket.readyState !== WebSocket.OPEN) return;
            const inputData = e.inputBuffer.getChannelData(0);
            const pcm16 = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                let s = Math.max(-1, Math.min(1, inputData[i]));
                pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }
            liveSocket.send(pcm16.buffer);
        };
    }

    function playAudioBase64(b64) {
        if (!liveAudioCtx) return;
        const binaryString = window.atob(b64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        const pcm16 = new Int16Array(bytes.buffer);
        const float32 = new Float32Array(pcm16.length);
        for (let i = 0; i < pcm16.length; i++) {
            float32[i] = pcm16[i] / 32768;
        }
        const buffer = liveAudioCtx.createBuffer(1, float32.length, 16000);
        buffer.copyToChannel(float32, 0);
        
        const source = liveAudioCtx.createBufferSource();
        source.buffer = buffer;
        source.connect(liveAudioCtx.destination);
        
        const startTime = Math.max(liveAudioCtx.currentTime, nextPlayTime);
        source.start(startTime);
        nextPlayTime = startTime + buffer.duration;
    }

    function stopLiveVoice() {
        if (liveVoiceBtn) {
            liveVoiceBtn.style.color = "#10a37f";
            liveVoiceBtn.classList.remove("active");
        }
        if (liveProcessor) { liveProcessor.disconnect(); liveProcessor = null; }
        if (liveMicStream) { liveMicStream.getTracks().forEach(t => t.stop()); liveMicStream = null; }
        if (liveAudioCtx) { liveAudioCtx.close(); liveAudioCtx = null; }
        if (liveSocket && liveSocket.readyState === WebSocket.OPEN) { liveSocket.close(); }
        liveSocket = null;
        nextPlayTime = 0;
    }
});
