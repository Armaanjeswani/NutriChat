import React, { useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import { GiHamburgerMenu } from "react-icons/gi";
import Header from "../components/Header";
import { ChatData } from "../context/ChatContext";
import { CgProfile } from "react-icons/cg";
import { FaRobot } from "react-icons/fa";
import { LoadingBig, LoadingSmall } from "../components/Loading";
import { IoMdSend } from "react-icons/io";

const Home = () => {
  const [isOpen, setIsOpen] = React.useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const {
    messages,
    prompt,
    setPrompt,
    fetchResponse,
    newRequestLoading,
    loadingMessages,
    selectedChatId,
    createChat,
  } = ChatData();

  const submitHandler = (e) => {
    e.preventDefault();
    fetchResponse();
  };

  const messagecontainerRef = useRef();

  useEffect(() => {
    if (messagecontainerRef.current) {
      messagecontainerRef.current.scrollTo({
        top: messagecontainerRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar isOpen={isOpen} toggleSidebar={toggleSidebar} />

      <div className="flex flex-1 flex-col">
        <button
          onClick={toggleSidebar}
          className="md:hidden p-4 bg-gray-800 text-2xl"
        >
          <GiHamburgerMenu />
        </button>

        <div className="flex-1 p-6 mb-20 md:mb-0">
          <Header />

          {!selectedChatId ? (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-lg mb-4">Select or create a chat to start chatting!</p>
              <button
                onClick={createChat}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                New Chat
              </button>
            </div>
          ) : loadingMessages ? (
            <LoadingBig />
          ) : (
            <div
              className="flex-1 p-6 max-h-[600px] overflow-y-auto mb-20 md:mb-0 thin-scrollbar"
              ref={messagecontainerRef}
            >
              {messages && messages.length > 0 ? (
                messages.map((e, i) => (
                  <div key={i}>
                    {e.role === "user" ? (
                      <div className="mb-4 p-4 rounded bg-blue-700 text-white flex gap-1">
                        <div className="bg-white p-2 rounded-full text-black text-2xl h-10">
                          <CgProfile />
                        </div>
                        {e.content}
                      </div>
                    ) : (
                      <div className="mb-4 p-4 rounded bg-gray-700 text-white flex gap-1">
                        <div className="bg-white p-2 rounded-full text-black text-2xl h-10">
                          <FaRobot />
                        </div>
                        <p>{e.content}</p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p>No messages yet</p>
              )}
              {newRequestLoading && <LoadingSmall />}
            </div>
          )}
        </div>
      </div>

      {selectedChatId && (
        <div className="fixed bottom-0 right-0 left-auto p-4 bg-gray-900 w-full md:w-[75%]">
          <form
            onSubmit={submitHandler}
            className="flex justify-center items-center"
          >
            <input
              className="flex-grow p-4 bg-gray-700 rounded-l text-white outline-none"
              type="text"
              placeholder="Enter a prompt here"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              required
              disabled={newRequestLoading}
            />
            <button className="p-4 bg-gray-700 rounded-r text-2xl text-white" disabled={newRequestLoading}>
              <IoMdSend />
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Home;