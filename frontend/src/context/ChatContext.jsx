import axios from "axios";
import { createContext, useContext, useState, useEffect } from "react";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [newRequestLoading, setNewRequestLoading] = useState(false);
  const [loadingChats, setLoadingChats] = useState(false);
  const [loadingMessages, setLoadingMessages] = useState(false);

  // Fetch all chats
  async function fetchChats() {
    setLoadingChats(true);
    try {
      const response = await axios.get("http://localhost:8000/chats");
      setChats(response.data.chats);
      // Select the first chat if none selected
      if (response.data.chats.length > 0 && !selectedChatId) {
        setSelectedChatId(response.data.chats[0]._id);
      }
    } catch (error) {
      setChats([]);
    }
    setLoadingChats(false);
  }

  // Create a new chat
  async function createChat() {
    try {
      const response = await axios.post("http://localhost:8000/chats", { title: "New Chat" });
      await fetchChats();
      setSelectedChatId(response.data.chat_id);
      setMessages([]);
    } catch (error) {
      // Optionally handle error
    }
  }

  // Delete a chat
  async function deleteChat(chatId) {
    try {
      await axios.delete(`http://localhost:8000/chats/${chatId}`);
      await fetchChats();
      // If the deleted chat was selected, select another
      if (selectedChatId === chatId) {
        if (chats.length > 1) {
          const remaining = chats.filter(c => c._id !== chatId);
          setSelectedChatId(remaining[0]?._id || null);
        } else {
          setSelectedChatId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      // Optionally handle error
    }
  }

  // Select a chat
  function selectChat(chatId) {
    setSelectedChatId(chatId);
  }

  // Fetch messages for selected chat
  async function fetchMessages(chatId) {
    if (!chatId) return setMessages([]);
    setLoadingMessages(true);
    try {
      const response = await axios.get(`http://localhost:8000/chats/${chatId}/messages`);
      setMessages(response.data.messages);
    } catch (error) {
      setMessages([]);
    }
    setLoadingMessages(false);
  }

  // Send a new message to the selected chat
  async function fetchResponse() {
    if (!selectedChatId) return alert("Select or create a chat first");
    if (prompt === "") return alert("Write prompt");
    setNewRequestLoading(true);
    const userPrompt = prompt;
    setPrompt("");
    try {
      const response = await axios.post(`http://localhost:8000/chats/${selectedChatId}/messages`, {
        message: userPrompt,
      });
      // Refetch messages to get both user and bot message
      await fetchMessages(selectedChatId);
      setNewRequestLoading(false);
    } catch (error) {
      alert("Something went wrong");
      setNewRequestLoading(false);
    }
  }

  // Fetch chats on mount
  useEffect(() => {
    fetchChats();
  }, []);

  // Fetch messages when selected chat changes
  useEffect(() => {
    if (selectedChatId) {
      fetchMessages(selectedChatId);
    }
  }, [selectedChatId]);

  return (
    <ChatContext.Provider
      value={{
        chats,
        selectedChatId,
        selectChat,
        createChat,
        deleteChat,
        fetchChats,
        messages,
        fetchMessages,
        prompt,
        setPrompt,
        fetchResponse,
        newRequestLoading,
        loadingChats,
        loadingMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const ChatData = () => useContext(ChatContext);