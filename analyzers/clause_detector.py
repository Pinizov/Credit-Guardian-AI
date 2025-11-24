import re
from typing import List, Dict
from database.models import Session, UnfairClause

class ClauseDetector:
    """Детектор на неравноправни клаузи в договори"""
    
    def __init__(self):
        self.unfair_patterns = self._load_patterns()
        
    def _load_patterns(self) -> List[Dict]:
        """Зарежда шаблони на неравноправни клаузи"""
        
        patterns = [
            {
                'type': 'Едностранно изменение',
                'keywords': [
                    'кредиторът има право едностранно да промени',
                    'банката може да измени по всяко време',
                    'правото за промяна на условията',
                    'изменение без предварително уведомление'
                ],
                'legal_basis': 'чл. 143, ал. 1, т. 5 ЗЗП',
                'severity': 'high',
                'explanation': 'Клаузата позволява едностранно изменение на съществени условия'
            },
            {
                'type': 'Прекомерна неустойка',
                'keywords': [
                    'неустойка в размер на',
                    'договорна лихва.*процент',
                    'обезщетение за забава'
                ],
                'legal_basis': 'чл. 143, ал. 1, т. 3 ЗЗП',
                'severity': 'medium',
                'explanation': 'Неустойката може да е прекомерна спрямо претърпените вреди'
            },
            {
                'type': 'Ограничаване правото на предсрочно погасяване',
                'keywords': [
                    'предсрочното погасяване не се допуска',
                    'забрана за предсрочно погасяване',
                    'обезщетение за предсрочно.*процент'
                ],
                'legal_basis': 'чл. 29 ЗПК',
                'severity': 'critical',
                'explanation': 'Потребителят има право на предсрочно погасяване'
            },
        ]
        
        return patterns
    
    def detect_unfair_clauses(self, contract_text: str) -> List[Dict]:
        """Детектира неравноправни клаузи в договор"""
        
        detected_clauses = []
        
        for pattern in self.unfair_patterns:
            matches = self._find_pattern_matches(contract_text, pattern)
            
            if matches:
                for match in matches:
                    clause = {
                        'type': pattern['type'],
                        'text': match['text'],
                        'legal_basis': pattern['legal_basis'],
                        'severity': pattern['severity'],
                        'explanation': pattern['explanation'],
                        'context': match['context'],
                        'position': match['position']
                    }
                    detected_clauses.append(clause)
        
        return detected_clauses
    
    def _find_pattern_matches(self, text: str, pattern: Dict) -> List[Dict]:
        """Търси съвпадения на шаблон в текста"""
        
        matches = []
        text_lower = text.lower()
        
        for keyword in pattern['keywords']:
            regex = re.compile(keyword, re.IGNORECASE | re.DOTALL)
            
            for match in regex.finditer(text):
                start = match.start()
                end = match.end()
                
                context_start = max(0, start - 50)
                context_end = min(len(text), end + 50)
                context = text[context_start:context_end]
                
                sentence_start = text.rfind('.', 0, start) + 1
                sentence_end = text.find('.', end)
                if sentence_end == -1:
                    sentence_end = len(text)
                
                full_clause = text[sentence_start:sentence_end].strip()
                
                matches.append({
                    'text': full_clause,
                    'context': context,
                    'position': start,
                    'keyword': keyword
                })
        
        return matches
    
    def analyze_clause_severity(self, clauses: List[Dict]) -> Dict:
        """Анализира общата тежест на намерените клаузи"""
        
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for clause in clauses:
            severity = clause.get('severity', 'low')
            severity_counts[severity] += 1
        
        risk_score = (
            severity_counts['critical'] * 10 +
            severity_counts['high'] * 5 +
            severity_counts['medium'] * 2 +
            severity_counts['low'] * 1
        )
        
        if risk_score >= 20:
            overall_risk = 'critical'
        elif risk_score >= 10:
            overall_risk = 'high'
        elif risk_score >= 5:
            overall_risk = 'medium'
        else:
            overall_risk = 'low'
        
        return {
            'severity_counts': severity_counts,
            'risk_score': risk_score,
            'overall_risk': overall_risk,
            'total_clauses': len(clauses),
            'recommendation': self._get_recommendation(overall_risk)
        }
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Дава препоръка според риска"""
        
        recommendations = {
            'critical': 'СИЛНО НЕ ПРЕПОРЪЧВАМЕ подписване на този договор! '
                       'Съдържа сериозни нарушения на закона. '
                       'Консултирайте се с юрист незабавно.',
            
            'high': 'НЕ ПРЕПОРЪЧВАМЕ подписване без промени. '
                   'Договорът съдържа множество неравноправни клаузи. '
                   'Поискайте преразглеждане на условията.',
            
            'medium': 'ВНИМАНИЕ! Договорът съдържа проблемни клаузи. '
                     'Обсъдете условията с кредитора преди подписване.',
            
            'low': 'Договорът е относително приемлив, но прочетете внимателно '
                  'всички условия преди подписване.'
        }
        
        return recommendations.get(risk_level, '')
    
    def generate_complaint(self, clauses: List[Dict], creditor: str) -> str:
        """Генерира жалба до КЗП на база намерени клаузи"""
        
        from datetime import datetime
        
        complaint = f"""
ДО
КОМИСИЯТА ЗА ЗАЩИТА НА ПОТРЕБИТЕЛИТЕ

ЖАЛБА
от: [ИМЕ НА ПОТРЕБИТЕЛ]
срещу: {creditor}

Уважаеми дами и господа,

Подавам жалба срещу {creditor} за използване на неравноправни клаузи в договор 
за потребителски кредит, в нарушение на Закона за защита на потребителите.

УСТАНОВЕНИ НАРУШЕНИЯ:

"""
        
        for i, clause in enumerate(clauses, 1):
            complaint += f"""
{i}. {clause['type']}

Текст на клаузата:
"{clause['text']}"

Правно основание: {clause['legal_basis']}
Обяснение: {clause['explanation']}

"""
        
        complaint += f"""
На основание горепосоченото, моля да се образува производство и да се наложат 
предвидените в закона санкции на {creditor}.

Моля също така да се прогласи нищожността на неравноправните клаузи.

Дата: {datetime.now().strftime('%d.%m.%Y')}
Подпис: _________________
"""
        
        return complaint
