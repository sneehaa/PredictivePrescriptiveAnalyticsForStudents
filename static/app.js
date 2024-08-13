class Chatbot {
    constructor() {
        this.args = {
            openButton: document.querySelector(".chatbot__button"),
            chatBot: document.querySelector(".chatbot__support"),
            sendButton: document.querySelector(".chatbot__send--footer"),
            inputField: document.querySelector(".chatbot__support input"),
            chatMessageContainer: document.querySelector(".chatbot__messages"),
            deleteButton: document.querySelector(".chatbot__delete--button"),
            closeButton: document.querySelector(".chatbot__close--button"),
        };

        this.state = false; // false means the chatbox is initially hidden
        this.messages = this.loadMessages(); // Load messages from localStorage

        // Set up event listeners
        this.setupEventListeners();
        this.updateChatMessages(); // Load existing messages on page load
    }

    setupEventListeners() {
        const { openButton, sendButton, inputField, deleteButton, closeButton } = this.args;

        openButton.addEventListener("click", () => this.toggleState());
        sendButton.addEventListener("click", () => this.openSendButton());
        inputField.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.openSendButton();
            }
        });
        deleteButton.addEventListener("click", () => this.deleteMessages());
        closeButton.addEventListener("click", () => this.closeChatBox());
    }

    toggleState() {
        this.state = !this.state;
        if (this.state) {
            this.args.chatBot.style.display = "block";
            this.args.chatBot.querySelector('.chatbot__header').style.display = 'block';
            this.args.inputField.focus(); // Focus input field when opened
        } else {
            this.args.chatBot.style.display = "none";
            this.args.chatBot.querySelector('.chatbot__header').style.display = 'none';
        }
    }

    closeChatBox() {
        this.args.chatBot.style.display = "none";
        this.state = false;
    }

    openSendButton() {
        const textField = this.args.inputField;
        const text1 = textField.value.trim();
        if (text1 === "") {
            return;
        }

        const msg1 = { name: "User", message: text1 };
        this.messages.push(msg1);

        fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: JSON.stringify({ message: text1 }),
            mode: "cors",
            headers: {
                "Content-Type": "application/json",
            },
        })
          .then((response) => response.json())
          .then((data) => {
                const msg2 = { name: "Bot", message: data.answer };
                this.messages.push(msg2);
                this.saveMessages(); // Save messages after adding bot's response
                this.updateChatMessages(); // Update the chatbox with all messages
                textField.value = "";
            })
          .catch((error) => {
                console.error("Error:", error);
                this.saveMessages(); // Save messages even if there is an error
                this.updateChatMessages(); // Update the chatbox with all messages
                textField.value = "";
            });
    }

    updateChatMessages() {
        this.args.chatMessageContainer.innerHTML = ""; // Clear existing messages
        this.messages.forEach((message) => {
            const chatMessage = document.createElement("div");
            chatMessage.className = message.name === "User" ? "message message--user" : "message message--bot";
            chatMessage.innerHTML = `
                <div class="chatbot__image--message">
                    <img src="${
                        message.name === "User"
                          ? "https://img.icons8.com/color/48/000000/circled-user-female-skin-type-5--v1.png"
                            : "https://img.icons8.com/color/48/000000/circled-user-male-skin-type-5--v1.png"
                    }" alt="image">
                </div>
                <div class="chatbot__content--message">
                    <h4 class="chatbot__heading--message">${message.name}</h4>
                    <p class="chatbot__description--message">${message.message}</p>
                </div>
            `;
            this.args.chatMessageContainer.appendChild(chatMessage);
        });
        this.args.chatMessageContainer.scrollTop = this.args.chatMessageContainer.scrollHeight;
    }

    deleteMessages() {
        localStorage.removeItem("chatMessages");
        this.messages = [];
        this.updateChatMessages(); // Clear the chatbox
    }

    saveMessages() {
        localStorage.setItem("chatMessages", JSON.stringify(this.messages));
    }

    loadMessages() {
        const storedMessages = localStorage.getItem("chatMessages");
        return storedMessages ? JSON.parse(storedMessages) : [];
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const chatBot = new Chatbot();
});
