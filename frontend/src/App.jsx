import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import Dashboard from './components/Dashboard';
import CreditorSearch from './components/CreditorSearch';
import CreditorList from './components/CreditorList';
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
      case 'creditors':
        return <CreditorList />;
      case 'gpr':
        return <GPRCalculator />;
      case 'contract':
        return <ContractAnalyzer />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header with navigation */}
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 py-6">
          {/* Page Content */}
          <div className="animate-fade-in">
            {renderContent()}
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
