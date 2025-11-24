import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import CreditorSearch from './components/CreditorSearch';
import GPRCalculator from './components/GPRCalculator';
import ContractAnalyzer from './components/ContractAnalyzer';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'creditor':
        return <CreditorSearch />;
      case 'gpr':
        return <GPRCalculator />;
      case 'contract':
        return <ContractAnalyzer />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div>
      <div className="header">
        <div className="container">
          <h1>Credit Guardian</h1>
          <p>Система за защита на потребителите при кредитиране</p>
        </div>
      </div>

      <div className="container">
        <nav className="nav">
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Статистика
          </button>
          <button
            className={activeTab === 'creditor' ? 'active' : ''}
            onClick={() => setActiveTab('creditor')}
          >
            🔍 Проверка на кредитор
          </button>
          <button
            className={activeTab === 'gpr' ? 'active' : ''}
            onClick={() => setActiveTab('gpr')}
          >
            🧮 ГПР Калкулатор
          </button>
          <button
            className={activeTab === 'contract' ? 'active' : ''}
            onClick={() => setActiveTab('contract')}
          >
            📄 Анализ на договор
          </button>
        </nav>

        {renderContent()}
      </div>
    </div>
  );
}

export default App;
