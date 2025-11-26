import React from 'react';
import Card from './ui/Card';

/**
 * Trust indicators component - shows credibility and trust signals
 */
export default function TrustIndicators() {
  const indicators = [
    {
      icon: '🔒',
      title: '100% Безплатно',
      description: 'Всички функции са напълно безплатни, без скрити такси',
    },
    {
      icon: '⚖️',
      title: 'Правно Обосновано',
      description: 'Базирано на българското законодателство и съдебна практика',
    },
    {
      icon: '🛡️',
      title: 'Защита на Данните',
      description: 'GDPR съвместимо. Вашите данни са в безопасност',
    },
    {
      icon: '✅',
      title: 'Проверено',
      description: 'Използвано от хиляди потребители в България',
    },
    {
      icon: '📊',
      title: 'Актуални Данни',
      description: 'Регулярно обновявана база с кредитори и нарушения',
    },
    {
      icon: '🤝',
      title: 'Подкрепа',
      description: 'Безплатна подкрепа и съвети от експерти',
    },
  ];

  return (
    <section className="py-16 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Защо да ни се доверите?
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Credit Guardian е създаден с цел да защитава правата на потребителите
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {indicators.map((indicator, index) => (
            <Card
              key={index}
              className="p-6 text-center hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-2 border-transparent hover:border-blue-200"
            >
              <div className="text-4xl mb-3">{indicator.icon}</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {indicator.title}
              </h3>
              <p className="text-sm text-gray-600">
                {indicator.description}
              </p>
            </Card>
          ))}
        </div>

        {/* Additional Trust Signals */}
        <div className="mt-12 pt-12 border-t border-gray-200">
          <div className="grid sm:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-sm text-gray-600">Анализирани договори</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">5,000+</div>
              <div className="text-sm text-gray-600">Доволни потребители</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-sm text-gray-600">Точност на анализа</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

