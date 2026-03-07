import React, { useState } from 'react';

interface Todo {
  id: number;
  text: string;
  completed: boolean;
}

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Todo[]>([]);
  const [newTask, setNewTask] = useState<string>('');

  const handleAddTask = () => {
    if (newTask.trim()) {
      setTasks([...tasks, { id: Date.now(), text: newTask, completed: false }]);
      setNewTask('');
    }
  };

  const handleDeleteTask = (index: number) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleToggleTask = (id: number) => {
    setTasks(tasks.map((task) =>
      task.id === id ? { ...task, completed: !task.completed } : task
    ));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-center mb-8">Todo App</h1>
      <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
        <div className="flex items-center justify-between mb-4">
          <input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Add a new task..."
            className="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleAddTask}
            className="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 transition-colors"
          >
            Add
          </button>
        </div>
        <ul className="space-y-2">
          {tasks.map((task, index) => (
            <li key={task.id} className={`flex items-center justify-between p-4 ${task.completed ? 'bg-green-500 text-white' : 'bg-white'} rounded-lg`}>
              <span className={`flex-1 ${task.completed ? 'line-through' : ''}`}>
                {task.text}
              </span>
              <button onClick={() => handleDeleteTask(index)} className="text-red-500 hover:text-red-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default App;