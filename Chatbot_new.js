import React, { useState } from "react";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import SendIcon from "@mui/icons-material/Send";
import { IoMdClose } from "react-icons/io";
import { TranslationContext } from "../hooks/translation";
import "./css/Chatbot.css";

// This implements the chatbot

export function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const { translate } = React.useContext(TranslationContext); // Gets the context of the translation
  const [isOpen, setIsOpen] = useState(false);

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const newMessages = [...messages, { sender: "user", text: userInput }];
    setMessages(newMessages);

    try {
      // Send the user's input to the backend API
      const storedToken = localStorage.getItem("token");
      const myHeaders = new Headers();
      myHeaders.append("Authorization", `Bearer ${storedToken}`);

      const requestOptions = {
        method: "POST",
        headers: myHeaders,
        redirect: "follow",
      };

      // Add site from user
      const response = await fetch(
        `https://api-656930476914.europe-west1.run.app/api/v1.0/chat/?site_id=1&query=${userInput}`,
        requestOptions
      );

      const botMessage = (await response.text())
        .replaceAll('"', "")
        .replaceAll("[", "")
        .replaceAll("]", "")
        .replaceAll("\\n", "\n");

      setMessages([...newMessages, { sender: "bot", text: botMessage }]);
    } catch (error) {
      setMessages([
        ...newMessages,
        {
          sender: "bot",
          text: `${translate.Chatbot.sorry}`,
        },
      ]);
    }

    setUserInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  // Updated toggleChatbot function with reset logic
  const toggleChatbot = async () => {
    if (isOpen) {
      // Chatbot is being closed, reset the chat memory
      try {
        const storedToken = localStorage.getItem("token");
        const myHeaders = new Headers();
        myHeaders.append("Authorization", `Bearer ${storedToken}`);

        const requestOptions = {
          method: "POST", 
          headers: myHeaders,
          redirect: "follow",
        };

        await fetch(
          `https://api-656930476914.europe-west1.run.app/api/v1.0/chat/reset`, // <--- check if this is the correct endpoint for resetting chat memory in the backend
          requestOptions
        );
      } catch (error) {
        console.error("Failed to reset chat memory:", error);
      }
    }

    // Toggle the chatbot's open/closed state
    setIsOpen(!isOpen);
  };

  return (
    <div>
      {/* Chat icon */}
      <button className="chat-icon" onClick={toggleChatbot}>
        <QuestionAnswerIcon />
      </button>

      {/* Chatbot */}
      {isOpen && (
        <div className="chatbot-container">
          {/* Top bar */}
          <div className="chatbot-header">
            <span>Chat</span>
            {/* Close button */}
            <button className="close-button" onClick={toggleChatbot}>
              <IoMdClose size={28} />
            </button>
          </div>
          <div className="chatbot-allert">
            <p
              style={{
                fontSize: "14px",
                color: "#777",
                marginLeft: "5px",
                display: "block",
              }}
            >
              {translate.Chatbot.subtitle}
            </p>
          </div>

          <div className="chatbot-box">
            <div className="chatbot-messages">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={
                    msg.sender === "user"
                      ? "chat-message user-message"
                      : "chat-message bot-message"
                  }
                >
                  <p>{msg.text}</p>
                </div>
              ))}
            </div>
            <div className="chatbot-input-container">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyPress={handleKeyPress}
                className="chatbot-input"
                placeholder={translate.Chatbot.message}
              />
              <button onClick={handleSend} className="chatbot-send-button">
                <SendIcon />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;