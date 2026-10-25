import React, { useState, useEffect, useRef } from 'react';

// Helper function to render **bold** markdown text from the AI
const formatText = (text) => {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-bold">{part.slice(2, -2)}</strong>;
    }
    return part;
  });
};

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello John! I am ClinicPilot AI. How can I help you with clinic information, doctor recommendations, or appointments today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [bookings, setBookings] = useState([]);
  
  // Auto-scroll reference
  const messagesEndRef = useRef(null);

  const fetchBookings = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/bookings');
      const data = await res.json();
      setBookings(data.bookings || []);
    } catch (err) {
      console.error('Failed to fetch bookings:', err);
    }
  };

  useEffect(() => {
    fetchBookings();
    const interval = setInterval(fetchBookings, 5000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { role: 'user', content: input };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updatedMessages }),
      });
      const data = await res.json();
      setMessages([...updatedMessages, { role: 'assistant', content: data.response }]);
      fetchBookings(); 
    } catch (err) {
      setMessages([...updatedMessages, { role: 'assistant', content: 'Error: Failed to connect to backend server.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    // h-screen locks the app to the window height, stopping it from pushing the table down
    <div className="flex flex-col md:flex-row h-screen bg-gray-100 font-sans">
      
      {/* LEFT PANEL: Chat Interface */}
      <div className="w-full md:w-1/2 flex flex-col border-r border-gray-300 bg-white h-full">
        <header className="p-4 border-b bg-blue-700 text-white shadow-sm shrink-0">
          <h1 className="text-xl font-bold">ClinicPilot AI Assistant</h1>
          <p className="text-xs text-blue-200 mt-1">Logged in as: John Doe (Patient ID: P001)</p>
        </header>

        {/* Scrollable Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div 
                className={`max-w-[80%] p-3 rounded-2xl text-sm shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
                }`}
              >
                {formatText(msg.content)}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-500 p-3 rounded-2xl rounded-bl-none border border-gray-200 text-sm animate-pulse flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          {/* Invisible div to target for auto-scrolling */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <form onSubmit={handleSendMessage} className="p-4 border-t bg-white flex gap-2 shrink-0">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            placeholder="Type your message here..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-full text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Send
          </button>
        </form>
      </div>

      {/* RIGHT PANEL: Live Bookings Dashboard */}
      <div className="w-full md:w-1/2 flex flex-col h-full bg-gray-50">
        <header className="p-4 border-b bg-gray-800 text-white shadow-sm flex justify-between items-center shrink-0">
          <h2 className="text-xl font-bold">Live Bookings</h2>
          <button
            onClick={fetchBookings}
            className="text-xs bg-gray-700 hover:bg-gray-600 px-3 py-1.5 rounded transition-colors"
          >
            Refresh Data
          </button>
        </header>

        <div className="p-6 flex-1 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-100 text-gray-600 uppercase text-xs tracking-wider border-b">
                  <th className="py-3 px-4">Booking ID</th>
                  <th className="py-3 px-4">Doctor</th>
                  <th className="py-3 px-4">Treatment</th>
                  <th className="py-3 px-4">Date & Time</th>
                  <th className="py-3 px-4 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 text-sm">
                {bookings.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center py-8 text-gray-400">
                      No bookings found. Try booking via the chat agent!
                    </td>
                  </tr>
                ) : (
                  bookings.map((b) => (
                    <tr key={b.booking_id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 px-4 font-semibold text-blue-600">{b.booking_id}</td>
                      <td className="py-3 px-4 text-gray-800">{b.doctor_id}</td>
                      <td className="py-3 px-4 text-gray-800">{b.treatment_id}</td>
                      <td className="py-3 px-4 text-gray-800">
                        {b.booking_date} <br/> <span className="text-gray-500 text-xs">{b.booking_time}</span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span className="bg-green-100 text-green-800 text-xs px-2.5 py-1 rounded-full font-medium border border-green-200">
                          {b.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  );
}

export default App;