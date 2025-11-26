import React, { useState, useEffect } from 'react';
import { cn } from '../lib/utils';

/**
 * Header component with mobile menu support
 */
export default function Header({ activeTab, onTabChange }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Track scroll for header shadow
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems = [
    { id: 'home', label: '🏠 Начало', icon: '🏠' },
    { id: 'dashboard', label: '📊 Статистика', icon: '📊' },
    { id: 'creditor', label: '🔍 Проверка', icon: '🔍' },
    { id: 'creditors', label: '🏢 Кредитори', icon: '🏢' },
    { id: 'gpr', label: '🧮 ГПР', icon: '🧮' },
    { id: 'contract', label: '📄 Анализ', icon: '📄' },
  ];

  const handleNavClick = (id) => {
    onTabChange(id);
    setMobileMenuOpen(false);
  };

  return (
    <header
      className={cn(
        'sticky top-0 z-50 transition-all duration-300',
        scrolled ? 'bg-white/95 backdrop-blur-sm shadow-md' : 'bg-white'
      )}
    >
      {/* Main Header */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <span className="text-3xl">🛡️</span>
              <div>
                <h1 className="text-2xl font-bold cursor-pointer" onClick={() => onTabChange('home')}>
                  Credit Guardian
                </h1>
                <p className="text-white/80 text-sm hidden sm:block">
                  Вашият дигитален защитник при кредитиране
                </p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-2">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={cn(
                    'px-4 py-2 rounded-lg font-medium transition-all duration-200',
                    activeTab === item.id
                      ? 'bg-white text-primary-600'
                      : 'text-white/90 hover:bg-white/20'
                  )}
                >
                  {item.label}
                </button>
              ))}
            </nav>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 rounded-lg hover:bg-white/20 transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Меню"
            >
              <span className="text-2xl">
                {mobileMenuOpen ? '✕' : '☰'}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={cn(
          'lg:hidden overflow-hidden transition-all duration-300',
          mobileMenuOpen ? 'max-h-96' : 'max-h-0'
        )}
      >
        <nav className="bg-gray-50 border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 py-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={cn(
                  'w-full text-left px-4 py-3 rounded-lg font-medium transition-colors',
                  'flex items-center gap-3',
                  activeTab === item.id
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                )}
              >
                <span className="text-xl">{item.icon}</span>
                {item.label.replace(item.icon, '').trim()}
              </button>
            ))}
          </div>
        </nav>
      </div>

      {/* Subtitle Bar - Desktop only */}
      <div className="hidden lg:block bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-2">
          <p className="text-sm text-gray-600 text-center">
            💡 Анализира договори • ✅ Проверява ГПР • ⚠️ Открива нарушения • 📋 Генерира жалби
          </p>
        </div>
      </div>
    </header>
  );
}

