import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import CreditorSearch from './components/CreditorSearch';
import CreditorList from './components/CreditorList';
import GPRCalculator from './components/GPRCalculator';
import ContractAnalyzer from './components/ContractAnalyzer';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [showLanding, setShowLanding] = useState(true);

  const handleGetStarted = () => {
    setShowLanding(false);
    setActiveTab('dashboard');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return showLanding ? <LandingPage onGetStarted={handleGetStarted} /> : <Dashboard />;
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
        return showLanding ? <LandingPage onGetStarted={handleGetStarted} /> : <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header with navigation - hide on landing page */}
      {!showLanding && (
        <Header activeTab={activeTab} onTabChange={(tab) => {
          setActiveTab(tab);
          setShowLanding(false);
        }} />
      )}

      {/* Main Content */}
      <main className="flex-1">
        {showLanding && activeTab === 'home' ? (
          <LandingPage onGetStarted={handleGetStarted} />
        ) : (
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="animate-fade-in">
              {renderContent()}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}

export default App;
