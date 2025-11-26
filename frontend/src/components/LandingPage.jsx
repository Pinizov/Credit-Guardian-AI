import React, { useState, useEffect } from 'react';
import { getRootStats } from '../api/client';
import SubscriptionForm from './SubscriptionForm';
import TrustIndicators from './TrustIndicators';
import Button from './ui/Button';
import Card from './ui/Card';

/**
 * Modern Landing Page with trust indicators and subscription
 */
export default function LandingPage({ onGetStarted }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await getRootStats();
      setStats(data);
    } catch (error) {
      console.error('Stats error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-0 -right-4 w-72 h-72 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium mb-8 border border-white/20">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span>100% Безплатно • Без скрити такси</span>
            </div>

            {/* Main Heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Защитете се от
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-orange-300">
                несправедливи кредити
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-xl sm:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Credit Guardian анализира вашите кредитни договори, проверява ГПР, 
              открива нарушения и ви помага да защитите правата си.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Button
                onClick={onGetStarted}
                size="lg"
                className="bg-white text-blue-700 hover:bg-blue-50 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
              >
                <span className="text-2xl mr-2">🚀</span>
                Започнете Безплатно
              </Button>
              <Button
                onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
                variant="outline"
                size="lg"
                className="bg-transparent border-2 border-white text-white hover:bg-white/10"
              >
                Научете Повече
              </Button>
            </div>

            {/* Trust Stats */}
            {stats && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-4xl mx-auto">
                <div className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold mb-1">{stats.creditors || 0}+</div>
                  <div className="text-sm text-blue-200">Кредитори</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold mb-1">{stats.violations || 0}+</div>
                  <div className="text-sm text-blue-200">Нарушения</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold mb-1">{stats.court_cases || 0}+</div>
                  <div className="text-sm text-blue-200">Съдебни дела</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold mb-1">100%</div>
                  <div className="text-sm text-blue-200">Безплатно</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Trust Indicators Section */}
      <TrustIndicators />

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
              Защо Credit Guardian?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Мощен инструмент за защита на потребителските права при кредитиране
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">📄</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">Анализ на Договори</h3>
              <p className="text-gray-600">
                Автоматичен анализ на кредитни договори с AI. Открива незаконни такси, 
                неправилно изчислен ГПР и неравноправни клаузи.
              </p>
            </Card>

            {/* Feature 2 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">🧮</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">ГПР Калкулатор</h3>
              <p className="text-gray-600">
                Прецизно изчисляване на Годишния Процент на Разходите (ГПР) 
                с всички такси и лихви включени.
              </p>
            </Card>

            {/* Feature 3 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">🔍</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">Проверка на Кредитори</h3>
              <p className="text-gray-600">
                База данни с всички кредитори, техните нарушения, съдебни дела 
                и риск профили.
              </p>
            </Card>

            {/* Feature 4 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">⚖️</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">Правна База</h3>
              <p className="text-gray-600">
                Актуална правна база с всички закони, наредби и съдебни решения 
                за потребителски кредити.
              </p>
            </Card>

            {/* Feature 5 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">📋</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">Генериране на Жалби</h3>
              <p className="text-gray-600">
                Автоматично генериране на жалби до КЗП, БНБ или съда 
                с всички необходими данни и законови цитати.
              </p>
            </Card>

            {/* Feature 6 */}
            <Card className="text-center p-8 hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
              <div className="text-5xl mb-4">🛡️</div>
              <h3 className="text-2xl font-bold mb-3 text-gray-900">100% Безплатно</h3>
              <p className="text-gray-600">
                Всички функции са напълно безплатни. Няма скрити такси, 
                няма абонаменти, няма ограничения.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
              Как работи?
            </h2>
            <p className="text-xl text-gray-600">
              Три прости стъпки до защита на вашите права
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-4">
                1
              </div>
              <h3 className="text-xl font-bold mb-3">Качете Договора</h3>
              <p className="text-gray-600">
                Качете вашия кредитен договор (PDF, DOCX или TXT) 
                за автоматичен анализ.
              </p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-4">
                2
              </div>
              <h3 className="text-xl font-bold mb-3">Получете Анализ</h3>
              <p className="text-gray-600">
                Нашата AI система анализира договора и открива всички 
                нарушения и проблеми.
              </p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 text-white rounded-full text-2xl font-bold mb-4">
                3
              </div>
              <h3 className="text-xl font-bold mb-3">Защитете Правата Си</h3>
              <p className="text-gray-600">
                Получете готови жалби и препоръки как да защитите 
                правата си.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Subscription Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl sm:text-5xl font-bold mb-4">
            Оставете се информирани
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Абонирайте се за новини, съвети и актуализации за защита на потребителските права
          </p>
          <SubscriptionForm />
        </div>
      </section>
    </div>
  );
}

