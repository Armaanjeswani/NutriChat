import { ChatData } from "../context/ChatContext";
import { MdDelete } from "react-icons/md";
import { AiOutlinePlus } from "react-icons/ai";
import nutriLogo from "../assets/nutri-logo.svg";

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const {
    chats,
    selectedChatId,
    selectChat,
    createChat,
    deleteChat,
    loadingChats,
  } = ChatData();

  return (
    <div
      className={`fixed inset-0 bg-gray-800 p-4 transition-transform transform md:relative md:translate-x-0 md:w-1/4 md:block ${
        isOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <button
        className="md:hidden p-2 mb-4 bg-gray-700 rounded text-2xl"
        onClick={toggleSidebar}
      >
        X
      </button>
      <div className="flex flex-col items-center mb-6">
        <div className="text-2xl font-semibold flex justify-between items-center w-full">
          NutriChat
          <button
            onClick={createChat}
            className="ml-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center"
            title="New Chat"
          >
            <AiOutlinePlus size={20} />
          </button>
        </div>
      </div>
      <div className="max-h-[500px] overflow-y-auto mb-20 md:mb-0 thin-scrollbar">
        {loadingChats ? (
          <p>Loading chats...</p>
        ) : chats && chats.length > 0 ? (
          chats.map((chat) => (
            <div
              key={chat._id}
              className={`flex items-center justify-between py-2 px-2 rounded mb-2 cursor-pointer ${
                selectedChatId === chat._id
                  ? "bg-blue-700 text-white"
                  : "bg-gray-700 text-white hover:bg-gray-600"
              }`}
              onClick={() => selectChat(chat._id)}
            >
              <span className="truncate">
                {chat.title && chat.title !== "New Chat"
                  ? chat.title
                  : chat.created_at
                  ? (() => {
                      try {
                        return new Date(chat.created_at).toLocaleString();
                      } catch {
                        return "Untitled";
                      }
                    })()
                  : "Untitled"}
              </span>
              <button
                className="ml-2 px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 flex items-center justify-center"
                onClick={e => {
                  e.stopPropagation();
                  deleteChat(chat._id);
                }}
                title="Delete Chat"
              >
                <MdDelete size={18} />
              </button>
            </div>
          ))
        ) : (
          <p>No chats yet</p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;