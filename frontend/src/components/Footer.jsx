import React from 'react';

/**
 * Footer component
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();
  
  const links = {
    product: [
      { label: 'Функции', href: '/#features' },
      { label: 'ГПР Калкулатор', href: '/gpr' },
      { label: 'Анализ на договор', href: '/contract' },
      { label: 'API', href: '/api/docs' },
    ],
    legal: [
      { label: 'Поверителност', href: '/privacy' },
      { label: 'Условия за ползване', href: '/terms' },
      { label: 'GDPR', href: '/gdpr' },
    ],
    resources: [
      { label: 'Закон за потребителския кредит', href: 'https://lex.bg/laws/ldoc/2135530039', external: true },
      { label: 'Комисия за защита на потребителите', href: 'https://kzp.bg', external: true },
      { label: 'БНБ - Базов лихвен процент', href: 'https://bnb.bg', external: true },
    ],
  };

  return (
    <footer className="bg-gray-900 text-white">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl">🛡️</span>
              <span className="text-xl font-bold">Credit Guardian</span>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              AI-базирана защита от неравноправни кредитни договори. 
              Анализираме договори, откриваме нарушения и генерираме жалби.
            </p>
            
            {/* Social Links */}
            <div className="flex gap-4 mt-6">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Facebook</span>
                📘
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Twitter</span>
                🐦
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">LinkedIn</span>
                💼
              </a>
            </div>
          </div>
          
          {/* Product Links */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-4">
              Продукт
            </h4>
            <ul className="space-y-3">
              {links.product.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Legal Links */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-4">
              Правна информация
            </h4>
            <ul className="space-y-3">
              {links.legal.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-gray-400 hover:text-white transition-colors text-sm"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          
          {/* Resources Links */}
          <div>
            <h4 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-4">
              Полезни ресурси
            </h4>
            <ul className="space-y-3">
              {links.resources.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    target={link.external ? '_blank' : undefined}
                    rel={link.external ? 'noopener noreferrer' : undefined}
                    className="text-gray-400 hover:text-white transition-colors text-sm flex items-center gap-1"
                  >
                    {link.label}
                    {link.external && <span className="text-xs">↗</span>}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
      
      {/* Bottom Bar */}
      <div className="border-t border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-500 text-sm">
              © {currentYear} Credit Guardian. Всички права запазени.
            </p>
            <p className="text-gray-600 text-xs">
              Powered by 🤖 AI • Made with ❤️ in Bulgaria
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

