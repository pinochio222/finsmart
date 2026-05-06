"""
FinSmart AI Suggestion Engine
Generates intelligent financial recommendations based on user transaction patterns
"""

from datetime import date, timedelta
from django.db.models import Sum, Q, Count
from django.contrib.auth.models import User
from .models import Transaction, Budget, Goal, Category, AISuggestion
import random


class FinancialAnalyzer:
    """Analyze user financial data and generate AI-powered suggestions"""
    
    def __init__(self, user: User):
        self.user = user
        self.today = date.today()
        self.month_start = date(self.today.year, self.today.month, 1)
        self.current_txs = Transaction.objects.filter(
            user=user, 
            date__month=self.today.month, 
            date__year=self.today.year
        )
    
    def get_month_stats(self):
        """Calculate monthly income/expense statistics"""
        stats = {
            'total_income': 0,
            'total_expense': 0,
            'net_savings': 0,
            'savings_rate': 0,
            'category_breakdown': {},
        }
        
        income = self.current_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0
        expense = self.current_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0
        
        stats['total_income'] = int(income)
        stats['total_expense'] = int(expense)
        stats['net_savings'] = stats['total_income'] - stats['total_expense']
        
        if stats['total_income'] > 0:
            stats['savings_rate'] = round((stats['net_savings'] / stats['total_income']) * 100, 1)
        
        # Category breakdown
        categories = self.current_txs.filter(type='expense').values('category__name').annotate(
            amount=Sum('amount')
        ).order_by('-amount')
        
        for cat in categories:
            stats['category_breakdown'][cat['category__name'] or 'Khác'] = int(cat['amount'])
        
        return stats
    
    def get_previous_month_stats(self):
        """Get previous month data for comparison"""
        if self.today.month == 1:
            prev_date = date(self.today.year - 1, 12, 1)
        else:
            prev_date = date(self.today.year, self.today.month - 1, 1)
        
        prev_txs = Transaction.objects.filter(
            user=self.user,
            date__month=prev_date.month,
            date__year=prev_date.year
        )
        
        income = prev_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0
        expense = prev_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0
        
        return {
            'income': int(income),
            'expense': int(expense),
            'savings': int(income) - int(expense)
        }
    
    def generate_suggestions(self) -> list:
        """Generate all relevant suggestions with randomization"""
        all_suggestions = []
        
        stats = self.get_month_stats()
        prev_stats = self.get_previous_month_stats()
        
        # 1. Spending Alert
        if stats['total_expense'] > 0:
            all_suggestions.extend(self._spending_alert(stats, prev_stats))
        
        # 2. Category Analysis
        if stats['category_breakdown']:
            all_suggestions.extend(self._category_insights(stats))
        
        # 3. Anomaly Detection
        all_suggestions.extend(self._detect_anomalies(stats, prev_stats))
        
        # 4. Income Boost
        if stats['total_income'] > 0:
            all_suggestions.extend(self._income_optimization(stats))
        
        # 5. Smart Savings
        if stats['net_savings'] > 0:
            all_suggestions.append(self._smart_saving_tip(stats))
        
        # 6. Goal Progress
        goals = Goal.objects.filter(user=self.user)
        if goals.exists():
            all_suggestions.extend(self._goal_suggestions(goals))
        
        # 7. Budget Advice
        budgets = Budget.objects.filter(
            user=self.user, 
            month=self.today.month, 
            year=self.today.year
        )
        if not budgets.exists() and stats['total_expense'] > 0:
            all_suggestions.append(self._budget_advice(stats))
        
        # 8. Recurring Expense Analysis
        all_suggestions.extend(self._recurring_expense_analysis())
        
        # 9. Budget Optimization
        if stats['category_breakdown']:
            all_suggestions.extend(self._budget_optimization(stats))
        
        # 10. Savings Milestone
        all_suggestions.extend(self._savings_milestone(stats))
        
        # 11. Spending Pattern
        all_suggestions.extend(self._spending_pattern(stats))
        
        # 12. Category Trend
        all_suggestions.extend(self._category_trend(stats, prev_stats))
        
        # ⭐ 13. Budget ↔ Goal Linking Suggestions
        all_suggestions.extend(self._budget_goal_linking_suggestions())
        
        # ⭐ 14. Transaction ↔ Budget Analysis Suggestions
        all_suggestions.extend(self._budget_analysis_suggestions())
        
        # ⭐ 15. Transaction ↔ Goal Auto Update Suggestions
        all_suggestions.extend(self._goal_transaction_suggestions())
        
        # ⭐ 16. Goal Achievement Suggestions (Gợi ý về mục tiêu)
        all_suggestions.extend(self._goal_achievement_suggestions())
        
        # ⭐ 17. Savings Strategy Suggestions (Gợi ý tiết kiệm)
        all_suggestions.extend(self._savings_strategy_suggestions())
        
        # ⭐ 18. Debt Management Suggestions (Gợi ý quản lý nợ)
        all_suggestions.extend(self._debt_management_suggestions())
        
        # 19. Saving Tips (General) - Add 2-3 random tips
        for _ in range(random.randint(2, 3)):
            all_suggestions.append(self._general_saving_tips())
        
        # Filter out None values
        all_suggestions = [s for s in all_suggestions if s]
        
        # Return ALL suggestions (don't filter to 3 here)
        return all_suggestions
    
    def _spending_alert(self, stats: dict, prev_stats: dict) -> list:
        """Generate spending analysis alerts"""
        suggestions = []
        
        current_expense = stats['total_expense']
        prev_expense = prev_stats['expense']
        current_income = stats['total_income']
        
        # Alert if spending exceeds income
        if current_expense > current_income > 0:
            priority = 'high'
            savings_rate = stats['savings_rate']
            message = f'⚠️ Chi tiêu ({current_expense:,}đ) vượt thu nhập ({current_income:,}đ)! Tỷ lệ tiết kiệm: {savings_rate}%'
        else:
            priority = 'medium' if current_expense < current_income else 'high'
            savings_rate = stats['savings_rate']
            message = f'Tháng này bạn đã chi {current_expense:,}đ. Tỷ lệ tiết kiệm: {savings_rate}%'
        
        # Compare with previous month
        if prev_expense > 0:
            change_pct = round(((current_expense - prev_expense) / prev_expense) * 100, 1)
            if abs(change_pct) > 10:
                trend = 'tăng' if change_pct > 0 else 'giảm'
                message += f' (Chi tiêu {trend} {abs(change_pct)}% so với tháng trước)'
        
        suggestions.append(AISuggestion(
            user=self.user,
            type='spending_alert',
            priority=priority,
            title='Phân tích chi tiêu tháng này',
            message=message
        ))
        
        return suggestions
    
    def _category_insights(self, stats: dict) -> list:
        """Analyze spending by category"""
        suggestions = []
        
        breakdown = stats['category_breakdown']
        if not breakdown:
            return suggestions
        
        # Find top spending category
        top_cat = max(breakdown.items(), key=lambda x: x[1])
        top_name, top_amount = top_cat
        total_expense = stats['total_expense']
        
        if total_expense > 0:
            cat_pct = round((top_amount / total_expense) * 100, 1)
            
            if cat_pct > 40:
                priority = 'high'
                message = f'Danh mục "{top_name}" chiếm {cat_pct}% tổng chi tiêu ({top_amount:,}đ). Xem xét cân bằng lại ngân sách!'
            elif cat_pct > 25:
                priority = 'medium'
                message = f'Danh mục "{top_name}" là chi tiêu lớn nhất của bạn với {cat_pct}% ({top_amount:,}đ).'
            else:
                return suggestions
            
            suggestions.append(AISuggestion(
                user=self.user,
                type='category_insight',
                priority=priority,
                title=f'Phân tích danh mục: {top_name}',
                message=message
            ))
        
        return suggestions
    
    def _detect_anomalies(self, stats: dict, prev_stats: dict) -> list:
        """Detect unusual spending patterns"""
        suggestions = []
        
        current_expense = stats['total_expense']
        prev_expense = prev_stats['expense']
        
        if prev_expense > 0:
            change = ((current_expense - prev_expense) / prev_expense) * 100
            
            # Major spike
            if change > 30:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='anomaly_detect',
                    priority='high',
                    title='⚠️ Phát hiện chi tiêu bất thường',
                    message=f'Chi tiêu tăng vọt {change:.0f}% so với tháng trước ({prev_expense:,}đ → {current_expense:,}đ). Kiểm tra chi tiết!'
                ))
            # Significant decrease (good!)
            elif change < -20:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='anomaly_detect',
                    priority='low',
                    title='🎉 Bạn đang kiểm soát chi tiêu tốt!',
                    message=f'Chi tiêu giảm {abs(change):.0f}% so với tháng trước. Tiếp tục duy trì nhé!'
                ))
        
        return suggestions
    
    def _income_optimization(self, stats: dict) -> list:
        """Suggest income improvement opportunities"""
        suggestions = []
        
        total_income = stats['total_income']
        total_expense = stats['total_expense']
        
        if total_income > 0 and total_income < total_expense:
            shortfall = total_expense - total_income
            suggestions.append(AISuggestion(
                user=self.user,
                type='income_boost',
                priority='high',
                title=f'💡 Tăng thu nhập để cân bằng',
                message=f'Bạn cần tăng thu nhập thêm {shortfall:,}đ/tháng để điểm hòa vốn. Xem xét thêm dòng thu nhập phụ!'
            ))
        elif total_income > 0 and total_expense > 0 and total_income > total_expense * 2:
            suggestions.append(AISuggestion(
                user=self.user,
                type='income_boost',
                priority='low',
                title='✨ Thu nhập ổn định',
                message=f'Thu nhập của bạn gấp {round(total_income/total_expense, 1)}x chi tiêu! Hãy tận dụng tiềm năng tiết kiệm.'
            ))
        
        return suggestions
    
    def _smart_saving_tip(self, stats: dict) -> AISuggestion:
        """Generate personalized saving tips with variations"""
        savings_rate = stats['savings_rate']
        
        # Random emoji variations
        emoji_good = random.choice(['🌟', '✨', '👏', '💪'])
        emoji_improve = random.choice(['🎯', '💡', '⚡', '🚀'])
        emoji_warn = random.choice(['⚠️', '🔴', '📊', '💬'])
        
        if savings_rate >= 30:
            title = f'{emoji_good} Xuất sắc! Bạn là nhà tiết kiệm thông minh'
            message = f'Tỷ lệ tiết kiệm {savings_rate}% là tuyệt vời! Hãy tăng mục tiêu tiết kiệm và xem xét đầu tư thêm.'
            priority = 'low'
        elif savings_rate >= 20:
            title = f'{emoji_good} Tốt! Tiếp tục duy trì'
            message = f'Tỷ lệ tiết kiệm {savings_rate}% là tốt. Cố gắng tăng lên 30% để có tương lai tài chính an toàn hơn.'
            priority = 'low'
        elif savings_rate >= 10:
            title = f'{emoji_improve} Mục tiêu: 20% tỷ lệ tiết kiệm'
            message = f'Tỷ lệ tiết kiệm hiện tại {savings_rate}%. Hãy cố gắng tăng thêm để đạt mục tiêu 20%.'
            priority = 'medium'
        else:
            title = f'{emoji_warn} Tăng tỷ lệ tiết kiệm ngay'
            message = f'Tỷ lệ tiết kiệm chỉ {savings_rate}%. Hãy giảm chi tiêu hoặc tăng thu nhập để cân bằng tài chính.'
            priority = 'high'
        
        return AISuggestion(
            user=self.user,
            type='smart_saving',
            priority=priority,
            title=title,
            message=message
        )
    
    def _goal_suggestions(self, goals) -> list:
        """Generate goal progress suggestions"""
        suggestions = []
        
        for goal in goals[:2]:  # Top 2 goals
            pct = goal.percentage
            
            if pct >= 100:
                priority = 'low'
                message = f'🎉 Xin chúc mừng! Bạn đã hoàn thành mục tiêu "{goal.name}"!'
            elif pct >= 75:
                priority = 'low'
                message = f'Gần xong rồi! Bạn đã đạt {pct}% mục tiêu "{goal.name}". Chỉ còn {goal.remaining:,}đ nữa!'
            elif pct >= 50:
                priority = 'medium'
                message = f'Tiến độ tốt! Bạn đã đạt {pct}% mục tiêu "{goal.name}" ({int(goal.current_amount):,}đ / {int(goal.target_amount):,}đ).'
            else:
                priority = 'medium'
                needed = goal.monthly_required
                msg = f'Bạn đã đạt {pct}% mục tiêu "{goal.name}".'
                if needed:
                    msg += f' Cần tiết kiệm {needed:,}đ/tháng để hoàn thành trước hạn.'
                message = msg
            
            suggestions.append(AISuggestion(
                user=self.user,
                type='goal_progress',
                priority=priority,
                title=f'Mục tiêu: {goal.name}',
                message=message
            ))
        
        return suggestions
    
    def _budget_advice(self, stats: dict) -> AISuggestion:
        """Suggest budget setup"""
        suggested_budget = round(stats['total_expense'] * 1.1, -3)  # Round up to nearest 1000
        
        return AISuggestion(
            user=self.user,
            type='budget_advice',
            priority='medium',
            title='💰 Thiết lập ngân sách tháng',
            message=f'Dựa trên chi tiêu hiện tại ({stats["total_expense"]:,}đ), tôi gợi ý ngân sách là {int(suggested_budget):,}đ/tháng. Thiết lập ngân sách giúp kiểm soát chi tiêu tốt hơn!'
        )
    
    def _recurring_expense_analysis(self) -> list:
        """Analyze recurring/subscription expenses"""
        suggestions = []
        
        # Find transactions in last 3 months
        three_months_ago = self.today - timedelta(days=90)
        recent_txs = Transaction.objects.filter(
            user=self.user,
            type='expense',
            date__gte=three_months_ago
        ).order_by('-date')
        
        # Look for similar amounts (potential subscriptions)
        from django.db.models import Count, Q
        from collections import Counter
        
        amounts = [int(t.amount) for t in recent_txs]
        amount_counts = Counter(amounts)
        
        # Find amounts appearing 2+ times
        recurring = {amt: count for amt, count in amount_counts.items() if count >= 2}
        
        if recurring:
            total_recurring = sum(amt * count for amt, count in recurring.items())
            most_common = max(recurring.items(), key=lambda x: x[1])[0]
            
            suggestions.append(AISuggestion(
                user=self.user,
                type='recurring_expense',
                priority='medium',
                title='🔄 Phát hiện chi phí lặp lại',
                message=f'Tôi phát hiện {len(recurring)} khoản chi tiêu lặp lại (có thể là đơn vị subscriptions). Tổng chi phí lặp lại: {total_recurring:,}đ/tháng. Xem xét hủy những dịch vụ không cần thiết!'
            ))
        
        return suggestions
    
    def _budget_optimization(self, stats: dict) -> list:
        """Suggest budget optimization by category"""
        suggestions = []
        
        breakdown = stats['category_breakdown']
        if not breakdown:
            return suggestions
        
        total_expense = stats['total_expense']
        
        # Find category that could be reduced
        for cat_name, amount in list(breakdown.items())[:3]:
            pct = (amount / total_expense) * 100
            
            if pct > 20 and amount > 500000:  # >20% and > 500k
                reduction = round(amount * 0.1, -3)  # 10% reduction
                saved = int(reduction)
                
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='budget_optimization',
                    priority='medium',
                    title=f'📊 Tối ưu hóa: {cat_name}',
                    message=f'Danh mục "{cat_name}" chiếm {pct:.0f}% chi tiêu. Nếu giảm 10%, bạn có thể tiết kiệm {saved:,}đ/tháng!'
                ))
        
        return suggestions
    
    def _savings_milestone(self, stats: dict) -> list:
        """Celebrate savings milestones"""
        suggestions = []
        
        net_savings = stats['net_savings']
        
        milestones = [1000000, 5000000, 10000000, 20000000, 50000000]
        
        for milestone in milestones:
            if 0 < net_savings < milestone:
                remaining = milestone - net_savings
                progress_pct = (net_savings / milestone) * 100
                
                if progress_pct > 50:  # Near milestone
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='savings_milestone',
                        priority='low',
                        title=f'🎯 Gần tới mục tiêu {milestone:,}đ',
                        message=f'Bạn đã tích lũy {net_savings:,}đ ({progress_pct:.0f}% của {milestone:,}đ). Chỉ còn {remaining:,}đ nữa!'
                    ))
        
        return suggestions
    
    def _spending_pattern(self, stats: dict) -> list:
        """Analyze spending pattern by week"""
        suggestions = []
        
        # Get dates of transactions this month
        dates = list(self.current_txs.values_list('date', flat=True))
        
        if not dates:
            return suggestions
        
        # Calculate average spending per week
        weeks = {}
        for tx_date in dates:
            week_num = tx_date.isocalendar()[1]
            weeks[week_num] = weeks.get(week_num, 0) + 1
        
        max_week = max(weeks.values()) if weeks else 0
        min_week = min(weeks.values()) if weeks else 0
        
        if max_week > min_week * 1.5:  # Significant variation
            suggestions.append(AISuggestion(
                user=self.user,
                type='spending_pattern',
                priority='medium',
                title='📈 Mô hình chi tiêu không đều',
                message=f'Chi tiêu của bạn thay đổi từ tuần này sang tuần khác. Hãy cố gắng duy trì chi tiêu ổn định hàng tuần để dễ kiểm soát.'
            ))
        
        return suggestions
    
    def _category_trend(self, stats: dict, prev_stats: dict) -> list:
        """Analyze category spending trends"""
        suggestions = []
        
        current_breakdown = stats['category_breakdown']
        
        if not current_breakdown:
            return suggestions
        
        # Find top 2 categories
        top_cats = sorted(current_breakdown.items(), key=lambda x: x[1], reverse=True)[:2]
        
        for cat_name, amount in top_cats:
            # Check if category spending is stable or changing
            trend_msg = "duy trì ổn định"
            priority = "low"
            
            if amount > 3000000:
                trend_msg = "khá cao, hãy xem xét giảm"
                priority = "high"
            elif amount > 1500000:
                trend_msg = "lên cao, theo dõi kỹ"
                priority = "medium"
            
            suggestions.append(AISuggestion(
                user=self.user,
                type='category_trend',
                priority=priority,
                title=f'📊 Xu hướng: {cat_name}',
                message=f'Danh mục "{cat_name}" đang {trend_msg}. Chi tiêu hiện tại: {amount:,}đ.'
            ))
        
        return suggestions
    
    def _general_saving_tips(self) -> AISuggestion:
        """Rotate through general financial tips"""
        tips = [
            ('Quy tắc 50/30/20', 'Dành 50% cho nhu cầu, 30% cho mong muốn, 20% cho tiết kiệm và đầu tư.'),
            ('Pay Yourself First', 'Hãy tiết kiệm trước, chi tiêu sau. Điều chỉnh tự động để chuyển tiền tiết kiệm trước tiên.'),
            ('Emergency Fund', 'Xây dựng quỹ khẩn cấp 3-6 tháng chi phí sống. Đó là lưới an toàn tài chính!'),
            ('Track Mục Tiêu', 'Đặt mục tiêu tài chính cụ thể (mua nhà, xe, du lịch). Mục tiêu rõ ràng giúp bạn kiên trì.'),
            ('Cắt Giảm Chi Tiêu', 'Xem xét hủy đăng ký dịch vụ không dùng. Có thể tiết kiệm 500k-1M/tháng!'),
            ('30 Ngày Rule', 'Trước khi mua thứ gì, chờ 30 ngày. Nếu vẫn muốn thì mua, nếu không quên đi!'),
            ('Budget Weekly', 'Kiểm tra ngân sách hàng tuần thay vì chỉ cuối tháng. Nhanh chóng điều chỉnh nếu cần.'),
            ('Automated Savings', 'Thiết lập chuyển khoản tự động ngày bạn nhận lương. Không cần suy nghĩ!'),
        ]
        
        title, message = random.choice(tips)
        
        return AISuggestion(
            user=self.user,
            type='saving_tip',
            priority='low',
            title=f'💡 Mẹo: {title}',
            message=message
        )

    # ⭐ LIÊN KẾT 1: Budget ↔ Goal Suggestions
    def _budget_goal_linking_suggestions(self) -> list:
        """Gợi ý liên kết ngân sách với mục tiêu"""
        from .models import Goal, Budget
        suggestions = []
        
        # Tìm goal có linked_budget
        linked_goals = Goal.objects.filter(user=self.user, linked_budget__isnull=False)
        
        for goal in linked_goals:
            if not goal.on_track_for_deadline:
                # Cảnh báo nếu chậm tiến độ
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='high',
                    title=f'⚠️ Mục tiêu "{goal.name}" chậm tiến độ',
                    message=f'Bạn cần tiết kiệm {goal.monthly_required:,}đ/tháng nhưng chỉ tiết kiệm được {goal.monthly_savings_from_budget:,}đ. Hãy cắt giảm chi tiêu hoặc tăng thu nhập!'
                ))
            elif goal.on_track_for_deadline:
                # Khích lệ nếu đúng tiến độ
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='low',
                    title=f'✅ Mục tiêu "{goal.name}" đúng tiến độ',
                    message=f'Tuyệt vời! Bạn đang tiết kiệm {goal.monthly_savings_from_budget:,}đ/tháng, đủ để đạt mục tiêu {goal.target_amount:,}đ vào {goal.deadline}.'
                ))
        
        # Gợi ý liên kết goal với budget
        unlinked_goals = Goal.objects.filter(user=self.user, linked_budget__isnull=True)
        if unlinked_goals.exists():
            suggestions.append(AISuggestion(
                user=self.user,
                type='budget_advice',
                priority='medium',
                title='💡 Liên kết mục tiêu với ngân sách',
                message=f'Bạn có {unlinked_goals.count()} mục tiêu chưa liên kết với ngân sách. Liên kết để tự động theo dõi tiến độ!'
            ))
        
        return suggestions

    # ⭐ LIÊN KẾT 2: Transaction ↔ Budget Analysis
    def _budget_analysis_suggestions(self) -> list:
        """Gợi ý dựa trên phân tích chi tiêu"""
        from .models import Budget
        suggestions = []
        
        budgets = Budget.objects.filter(
            user=self.user,
            month=self.today.month,
            year=self.today.year
        )
        
        for budget in budgets:
            # Cảnh báo danh mục vượt
            overspend = budget.overspend_by_category
            if overspend:
                for item in overspend[:2]:  # Top 2 danh mục vượt
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='spending_alert',
                        priority='high',
                        title=f'🚨 {item["category"]} vượt ngân sách',
                        message=f'Danh mục "{item["category"]}" đã vượt {item["overspend"]:,}đ. Hãy cắt giảm chi tiêu trong danh mục này!'
                    ))
            
            # Gợi ý ngân sách hàng ngày
            if budget.daily_budget_remaining > 0:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='budget_advice',
                    priority='low',
                    title=f'📊 Ngân sách hàng ngày',
                    message=f'Bạn có thể chi {budget.daily_budget_remaining:,}đ/ngày cho danh mục "{budget.category.name if budget.category else "tổng"}" để không vượt ngân sách.'
                ))
            
            # Cảnh báo nếu ngân sách quá chặt
            if budget.is_budget_reasonable is False:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='budget_optimization',
                    priority='medium',
                    title=f'⚠️ Ngân sách quá chặt',
                    message=f'Ngân sách tháng này ({budget.amount:,}đ) thấp hơn 20% so với chi tiêu thực tế tháng trước. Hãy điều chỉnh để thực tế hơn.'
                ))
        
        return suggestions

    # ⭐ LIÊN KẾT 3: Goal Progress Analysis
    def _goal_transaction_suggestions(self) -> list:
        """Gợi ý dựa trên tiến độ mục tiêu"""
        from .models import Goal
        suggestions = []
        
        # Tìm tất cả goal của user
        goals = Goal.objects.filter(user=self.user)
        
        for goal in goals:
            progress_pct = goal.percentage
            
            if progress_pct == 0:
                # Khích lệ bắt đầu
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='medium',
                    title=f'💰 Bắt đầu tiết kiệm cho "{goal.name}"',
                    message=f'Mục tiêu "{goal.name}" chưa có tiến độ. Hãy bắt đầu tiết kiệm ngay!'
                ))
            else:
                # Hiển thị tiến độ
                if progress_pct >= 75:
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='savings_milestone',
                        priority='low',
                        title=f'🎉 Gần hoàn thành "{goal.name}"',
                        message=f'Bạn đã đạt {progress_pct}% mục tiêu! Chỉ còn {goal.remaining:,}đ nữa là xong.'
                    ))
                elif progress_pct >= 50:
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='goal_progress',
                        priority='low',
                        title=f'✅ Tiến độ "{goal.name}" tốt',
                        message=f'Bạn đã tiết kiệm {goal.current_amount:,}đ ({progress_pct}%). Tiếp tục cố gắng!'
                    ))
        
        return suggestions

    def _goal_achievement_suggestions(self) -> list:
        """Gợi ý về mục tiêu tiết kiệm"""
        from .models import Goal
        suggestions = []
        
        goals = Goal.objects.filter(user=self.user)
        
        if not goals.exists():
            # Gợi ý tạo mục tiêu
            if self.get_month_stats()['net_savings'] > 0:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='medium',
                    title='🎯 Hãy tạo mục tiêu tiết kiệm',
                    message=f'Bạn có dư tiền {self.get_month_stats()["net_savings"]:,}đ tháng này. Hãy tạo mục tiêu để quản lý tiền tiết kiệm hiệu quả hơn!'
                ))
        else:
            # Phân tích tiến độ mục tiêu
            total_target = sum(int(g.target_amount) for g in goals)
            total_current = sum(int(g.current_amount) for g in goals)
            overall_progress = round((total_current / total_target) * 100, 1) if total_target > 0 else 0
            
            if overall_progress >= 80:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='savings_milestone',
                    priority='low',
                    title='🌟 Bạn đang tiết kiệm tốt!',
                    message=f'Tổng tiến độ mục tiêu của bạn đạt {overall_progress}%. Hãy tiếp tục duy trì thói quen tốt này!'
                ))
            elif overall_progress >= 50:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='medium',
                    title='📈 Tiến độ mục tiêu ổn định',
                    message=f'Bạn đã hoàn thành {overall_progress}% tổng mục tiêu. Tăng tốc độ tiết kiệm để đạt mục tiêu sớm hơn!'
                ))
            else:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='high',
                    title='⏰ Cần tăng tốc tiết kiệm',
                    message=f'Bạn mới hoàn thành {overall_progress}% mục tiêu. Hãy nạp thêm tiền từ tổng số dư để đạt mục tiêu đúng hạn!'
                ))
        
        return suggestions

    def _savings_strategy_suggestions(self) -> list:
        """Gợi ý chiến lược tiết kiệm"""
        suggestions = []
        stats = self.get_month_stats()
        prev_stats = self.get_previous_month_stats()
        
        # Chỉ so sánh nếu tháng trước có dữ liệu (prev_stats['income'] > 0)
        if prev_stats['income'] > 0:
            # Nếu tiết kiệm tăng so với tháng trước
            if stats['net_savings'] > prev_stats['savings']:
                increase = stats['net_savings'] - prev_stats['savings']
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='savings_milestone',
                    priority='low',
                    title='💪 Tiết kiệm tăng so với tháng trước',
                    message=f'Bạn tiết kiệm thêm {increase:,}đ so với tháng trước! Hãy duy trì thói quen tốt này.'
                ))
            
            # Nếu tiết kiệm giảm so với tháng trước
            elif stats['net_savings'] < prev_stats['savings']:
                decrease = prev_stats['savings'] - stats['net_savings']
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='budget_optimization',
                    priority='high',
                    title='⚠️ Tiết kiệm giảm so với tháng trước',
                    message=f'Bạn tiết kiệm ít hơn {decrease:,}đ so với tháng trước. Hãy kiểm tra chi tiêu và cắt giảm nếu cần.'
                ))
            
            # Nếu tiết kiệm bằng nhau
            else:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='low',
                    title='➡️ Tiết kiệm ổn định',
                    message=f'Tiết kiệm của bạn ổn định so với tháng trước ({stats["net_savings"]:,}đ). Hãy cố gắng tăng thêm!'
                ))
        
        # Gợi ý tỷ lệ tiết kiệm
        if stats['total_income'] > 0:
            if stats['savings_rate'] >= 30:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='savings_milestone',
                    priority='low',
                    title='🎖️ Tỷ lệ tiết kiệm xuất sắc',
                    message=f'Bạn tiết kiệm {stats["savings_rate"]}% thu nhập! Đây là tỷ lệ rất tốt. Tiếp tục cố gắng!'
                ))
            elif stats['savings_rate'] >= 20:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='goal_progress',
                    priority='low',
                    title='✅ Tỷ lệ tiết kiệm tốt',
                    message=f'Bạn tiết kiệm {stats["savings_rate"]}% thu nhập. Đây là mục tiêu hợp lý. Hãy duy trì!'
                ))
            elif stats['savings_rate'] > 0:
                suggestions.append(AISuggestion(
                    user=self.user,
                    type='budget_optimization',
                    priority='medium',
                    title='📊 Tỷ lệ tiết kiệm cần cải thiện',
                    message=f'Bạn chỉ tiết kiệm {stats["savings_rate"]}% thu nhập. Hãy cố gắng tăng lên ít nhất 20%.'
                ))
        
        return suggestions

    def _debt_management_suggestions(self) -> list:
        """Gợi ý quản lý nợ"""
        suggestions = []
        stats = self.get_month_stats()
        
        # Phát hiện chi tiêu vượt thu nhập (dấu hiệu nợ)
        if stats['total_income'] > 0 and stats['net_savings'] < 0:
            deficit = abs(stats['net_savings'])
            suggestions.append(AISuggestion(
                user=self.user,
                type='budget_optimization',
                priority='high',
                title='🚨 Chi tiêu vượt thu nhập',
                message=f'Bạn chi tiêu vượt {deficit:,}đ so với thu nhập! Hãy cắt giảm chi tiêu ngay để tránh nợ.'
            ))
        
        # Phân tích danh mục chi tiêu cao
        if stats['category_breakdown']:
            top_category = max(stats['category_breakdown'].items(), key=lambda x: x[1])
            category_name, category_amount = top_category
            
            if stats['total_expense'] > 0:
                category_pct = round((category_amount / stats['total_expense']) * 100, 1)
                
                if category_pct > 50:
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='budget_optimization',
                        priority='high',
                        title=f'⚠️ Danh mục "{category_name}" quá cao',
                        message=f'Danh mục "{category_name}" chiếm {category_pct}% chi tiêu ({category_amount:,}đ). Hãy kiểm tra và cắt giảm nếu có thể.'
                    ))
                elif category_pct > 40:
                    suggestions.append(AISuggestion(
                        user=self.user,
                        type='budget_optimization',
                        priority='medium',
                        title=f'📌 Danh mục "{category_name}" cần chú ý',
                        message=f'Danh mục "{category_name}" chiếm {category_pct}% chi tiêu. Hãy xem xét cắt giảm một chút.'
                    ))
        
        # Gợi ý tạo ngân sách để kiểm soát chi tiêu
        budgets = Budget.objects.filter(
            user=self.user,
            month=self.today.month,
            year=self.today.year
        )
        
        if not budgets.exists() and stats['total_expense'] > 0:
            suggestions.append(AISuggestion(
                user=self.user,
                type='budget_advice',
                priority='medium',
                title='📋 Hãy tạo ngân sách',
                message=f'Bạn chưa có ngân sách cho tháng này. Hãy tạo ngân sách để kiểm soát chi tiêu tốt hơn.'
            ))
        
        return suggestions


def generate_ai_suggestions(user: User) -> list:
    """Main function to generate all suggestions for a user"""
    analyzer = FinancialAnalyzer(user)
    return analyzer.generate_suggestions()


def generate_ai_suggestions_all_months(user: User) -> list:
    """Generate suggestions for all months with data"""
    all_suggestions = []
    
    # Get all months with transactions
    transactions = Transaction.objects.filter(user=user).values_list('date', flat=True).distinct()
    
    if not transactions:
        return []
    
    # Get unique months
    months_set = set()
    for tx_date in transactions:
        months_set.add((tx_date.year, tx_date.month))
    
    # Sort months in descending order (newest first)
    months_list = sorted(months_set, reverse=True)
    
    # Generate suggestions for each month
    for year, month in months_list:
        analyzer = FinancialAnalyzer(user)
        
        # Override current month/year
        analyzer.today = date(year, month, 1)
        analyzer.month_start = date(year, month, 1)
        analyzer.current_txs = Transaction.objects.filter(
            user=user,
            date__month=month,
            date__year=year
        )
        
        # Generate suggestions for this month
        suggestions = analyzer.generate_suggestions()
        all_suggestions.extend(suggestions)
    
    return all_suggestions


def seed_suggestions(user: User):
    """Clear old suggestions and generate new ones"""
    # Delete ALL suggestions for this user (not just old ones)
    # This ensures only 3 suggestions are displayed at any time
    AISuggestion.objects.filter(user=user).delete()
    
    # Generate new suggestions
    suggestions = generate_ai_suggestions(user)
    AISuggestion.objects.bulk_create(suggestions)


def seed_suggestions_all_months(user: User):
    """Generate suggestions for all months with data"""
    # Delete ALL suggestions for this user
    AISuggestion.objects.filter(user=user).delete()
    
    # Generate suggestions for all months
    suggestions = generate_ai_suggestions_all_months(user)
    AISuggestion.objects.bulk_create(suggestions)


def generate_ai_powered_suggestions(user: User, month: int, year: int) -> list:
    """
    Generate suggestions using REAL AI (Groq API)
    This function uses LLaMA 3.3 70B to analyze financial data and create personalized suggestions
    """
    import os
    from datetime import date
    from django.db.models import Sum
    
    try:
        import groq
    except ImportError:
        # Fallback to rule-based if groq not available
        return generate_ai_suggestions(user)
    
    # Get financial data for the month
    month_txs = Transaction.objects.filter(user=user, date__month=month, date__year=year)
    income = int(month_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
    expense = int(month_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)
    balance = income - expense
    savings_rate = round((balance / income) * 100, 1) if income > 0 else 0
    
    # Get category breakdown
    cat_breakdown = {}
    for tx in month_txs.filter(type='expense').select_related('category'):
        cat = tx.category.name if tx.category else 'Khác'
        cat_breakdown[cat] = cat_breakdown.get(cat, 0) + int(tx.amount)
    
    cat_str = ', '.join([f"{k}: {v:,}đ" for k, v in cat_breakdown.items()]) or 'Chưa có'
    
    # Get goals
    goals = Goal.objects.filter(user=user)
    goals_str = ', '.join([f"{g.name} ({int(g.current_amount):,}/{int(g.target_amount):,}đ)" for g in goals]) or 'Chưa có'
    
    # Get budgets
    budgets = Budget.objects.filter(user=user, month=month, year=year)
    budget_str = ''
    for b in budgets:
        cat_name = b.category.name if b.category else 'Tổng'
        budget_str += f"{cat_name}: {int(b.amount):,}đ (đã chi {b.spent:,}đ, {b.percentage}%), "
    budget_str = budget_str or 'Chưa có'
    
    # Create context for AI
    context = f"""Phân tích tài chính tháng {month}/{year}:

THU CHI:
- Thu nhập: {income:,}đ
- Chi tiêu: {expense:,}đ
- Số dư: {balance:,}đ
- Tỷ lệ tiết kiệm: {savings_rate}%

CHI TIÊU THEO DANH MỤC:
{cat_str}

NGÂN SÁCH:
{budget_str}

MỤC TIÊU TIẾT KIỆM:
{goals_str}

Hãy phân tích và đưa ra 5-7 gợi ý tài chính cụ thể, thiết thực cho người dùng. Mỗi gợi ý cần có:
1. Tiêu đề ngắn gọn (tối đa 50 ký tự)
2. Nội dung chi tiết (80-150 ký tự)
3. Mức độ ưu tiên (high/medium/low)
4. Loại gợi ý (spending_alert/saving_tip/goal_progress/budget_advice/category_insight)

Format: [PRIORITY]|[TYPE]|[TITLE]|[MESSAGE]
Ví dụ: high|spending_alert|Chi tiêu vượt thu nhập|Bạn chi {expense}đ vượt thu {income}đ. Cần cắt giảm ngay!"""
    
    try:
        # Call Groq API
        client = groq.Groq(api_key=os.environ.get('GROQ_API_KEY', ''))
        
        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {
                    'role': 'system',
                    'content': 'Bạn là chuyên gia tài chính cá nhân. Phân tích dữ liệu và đưa ra gợi ý ngắn gọn, cụ thể bằng tiếng Việt.'
                },
                {
                    'role': 'user',
                    'content': context
                }
            ],
            max_tokens=800,
            temperature=0.7,
        )
        
        ai_response = completion.choices[0].message.content
        
        # Parse AI response
        suggestions = []
        for line in ai_response.strip().split('\n'):
            line = line.strip()
            if not line or not '|' in line:
                continue
            
            try:
                parts = line.split('|')
                if len(parts) >= 4:
                    priority = parts[0].strip().lower()
                    sug_type = parts[1].strip()
                    title = parts[2].strip()
                    message = parts[3].strip()
                    
                    # Validate priority
                    if priority not in ['high', 'medium', 'low']:
                        priority = 'medium'
                    
                    # Validate type
                    valid_types = ['spending_alert', 'saving_tip', 'goal_progress', 'budget_advice', 
                                   'category_insight', 'anomaly_detect', 'income_boost', 'smart_saving',
                                   'recurring_expense', 'budget_optimization', 'savings_milestone',
                                   'spending_pattern', 'category_trend']
                    if sug_type not in valid_types:
                        sug_type = 'budget_advice'
                    
                    suggestions.append(AISuggestion(
                        user=user,
                        type=sug_type,
                        priority=priority,
                        title=title[:200],  # Limit title length
                        message=message[:500]  # Limit message length
                    ))
            except Exception as e:
                continue
        
        # If AI didn't generate enough suggestions, add some rule-based ones
        if len(suggestions) < 3:
            analyzer = FinancialAnalyzer(user)
            analyzer.today = date(year, month, 1)
            analyzer.month_start = date(year, month, 1)
            analyzer.current_txs = month_txs
            rule_based = analyzer.generate_suggestions()
            suggestions.extend(rule_based[:5 - len(suggestions)])
        
        return suggestions[:7]  # Return max 7 suggestions
        
    except Exception as e:
        # Fallback to rule-based if AI fails
        print(f"AI suggestion generation failed: {e}")
        analyzer = FinancialAnalyzer(user)
        analyzer.today = date(year, month, 1)
        analyzer.month_start = date(year, month, 1)
        analyzer.current_txs = month_txs
        return analyzer.generate_suggestions()[:7]


def seed_ai_suggestions_for_month(user: User, month: int, year: int):
    """Generate AI-powered suggestions for a specific month"""
    # Delete old suggestions for this month
    AISuggestion.objects.filter(
        user=user,
        created_at__month=month,
        created_at__year=year
    ).delete()
    
    # Generate AI-powered suggestions
    suggestions = generate_ai_powered_suggestions(user, month, year)
    
    # Save to database
    if suggestions:
        AISuggestion.objects.bulk_create(suggestions)
