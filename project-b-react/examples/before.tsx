import React, { useState } from 'react';
import { Button, Input, Text } from '@chakra-ui/react';
import { useColorMode } from '@chakra-ui/react';

const App = () => {
  const [todo, setTodo] = useState('');
  const [todos, setTodos] = useState([]);
  const { colorMode, toggleColorMode } = useColorMode();

  const handleAddTodo = () => {
    if (todo.trim() !== '') {
      setTodos([...todos, { id: Date.now(), text: todo, completed: false }]);
      setTodo('');
    }
  };

  const handleToggleTodo = (id) => {
    setTodos(todos.map((todo) =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl font-bold mb-4">{colorMode === 'light' ? 'Todo App' : 'Todo App (Dark Mode)'}</h1>
      <Input
        type="text"
        value={todo}
        onChange={(e) => setTodo(e.target.value)}
        placeholder="Add a new todo"
        className="mb-4"
      />
      <Button
        onClick={handleAddTodo}
        className="bg-blue-500 text-white hover:bg-blue-600 focus:outline-none"
      >
        Add
      </Button>
      <ul className="mt-4">
        {todos.map((todo) => (
          <li key={todo.id} className={`list-item ${todo.completed ? 'line-through' : ''}`}>
            <input type="checkbox" checked={todo.completed} onChange={() => handleToggleTodo(todo.id)} />
            {todo.text}
          </li>
        ))}
      </ul>
      <button onClick={toggleColorMode} className="bg-gray-500 text-white hover:bg-gray-600 focus:outline-none mt-4">
        {colorMode === 'light' ? 'Dark Mode' : 'Light Mode'}
      </button>
    </div>
  );
};

export default App;