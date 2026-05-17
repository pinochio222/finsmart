from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.contrib.auth.hashers import make_password
from .models import Category, Transaction, Budget, Goal, UserProfile
from datetime import date

COMMON_PASSWORDS = [
    '12345678', '123456789', '1234567890', 'password', 'admin', 'user',
    'test', 'demo', 'qwerty', 'abc123', '111111', '000000'
]


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, label='Tên đăng nhập',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập email hoặc tên đăng nhập',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'autocomplete': 'current-password',
        })
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100, label='Họ tên',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nguyễn Văn A',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'sv@example.com',
            'autocomplete': 'email',
        })
    )
    password1 = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tối thiểu 8 ký tự',
            'autocomplete': 'new-password',
            'id': 'id_password1',
        })
    )
    password2 = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu',
            'autocomplete': 'new-password',
            'id': 'id_password2',
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        
        # Kiểm tra email đã tồn tại
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email này đã được đăng ký. Vui lòng dùng email khác.')
        
        # Kiểm tra username (email) đã tồn tại
        if User.objects.filter(username=email).exists():
            raise ValidationError('Tài khoản này đã tồn tại. Vui lòng dùng email khác.')
        
        return email

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if len(name) < 2:
            raise ValidationError('Họ tên phải có ít nhất 2 ký tự.')
        return name

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if len(password) < 8:
            raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự.')
        if password.isdigit():
            raise ValidationError('Mật khẩu không được chứa toàn số. Hãy thêm chữ cái.')
        if password.lower() in COMMON_PASSWORDS:
            raise ValidationError('Mật khẩu quá phổ biến và dễ đoán. Hãy chọn mật khẩu khác.')
        if len(set(password)) < 4:
            raise ValidationError('Mật khẩu quá đơn giản. Hãy dùng ký tự đa dạng hơn.')
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1', '')
        password2 = self.cleaned_data.get('password2', '')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Hai mật khẩu không khớp nhau.')
        return password2

    def _post_clean(self):
        # Skip UserCreationForm._post_clean() which re-runs Django's password
        # validators and causes duplicate error messages. Our clean_password1()
        # already handles all validation with Vietnamese messages.
        super(UserCreationForm, self)._post_clean()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data['email'].lower().strip()
        user.email = self.cleaned_data['email'].lower().strip()
        user.first_name = self.cleaned_data['first_name'].strip()
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Mật khẩu không khớp')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AdminUserUpdateForm(forms.ModelForm):
    password = forms.CharField(label='Mật khẩu mới (để trống nếu không đổi)', required=False, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Email này đã được sử dụng')
        return email

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'color']
        labels = {
            'name': 'Tên danh mục',
            'type': 'Loại',
            'color': 'Màu sắc'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'description', 'note', 'date', 'category']
        labels = {
            'type': 'Loại', 'amount': 'Số tiền (đ)', 'description': 'Mô tả',
            'note': 'Ghi chú', 'date': 'Ngày', 'category': 'Danh mục'
        }
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1000', 'step': '1000'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            from django.db.models import Q
            # Hiển thị cả danh mục của user VÀ danh mục mặc định (khớp với trang /categories/)
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_default=True)
            ).order_by('type', 'name')


class BulkTransactionForm(forms.Form):
    """Form để nhập hàng loạt giao dịch"""
    transactions_data = forms.CharField(
        label='Dữ liệu giao dịch (CSV)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Định dạng: ngày,loại,số tiền,danh mục,mô tả\nVí dụ:\n15/1/2026,expense,500000,Ăn uống,Cơm trưa\n20/1/2026,income,10000000,Lương,Lương tháng 1'
        }),
        help_text='Mỗi dòng là một giao dịch. Định dạng: ngày (dd/mm/yyyy), loại (income/expense), số tiền, danh mục, mô tả'
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_transactions_data(self):
        data = self.cleaned_data.get('transactions_data', '').strip()
        if not data:
            raise ValidationError('Vui lòng nhập dữ liệu giao dịch')
        
        lines = data.split('\n')
        transactions = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 5:
                raise ValidationError(f'Dòng {i}: Thiếu dữ liệu. Cần: ngày, loại, số tiền, danh mục, mô tả')
            
            try:
                tx_date = date.strptime(parts[0], '%d/%m/%Y')
            except ValueError:
                raise ValidationError(f'Dòng {i}: Ngày không hợp lệ. Định dạng: dd/mm/yyyy')
            
            tx_type = parts[1].lower()
            if tx_type not in ['income', 'expense']:
                raise ValidationError(f'Dòng {i}: Loại phải là "income" hoặc "expense"')
            
            try:
                amount = int(parts[2])
                if amount <= 0:
                    raise ValueError
            except ValueError:
                raise ValidationError(f'Dòng {i}: Số tiền phải là số dương')
            
            category_name = parts[3]
            description = parts[4]
            
            transactions.append({
                'date': tx_date,
                'type': tx_type,
                'amount': amount,
                'category_name': category_name,
                'description': description
            })
        
        if not transactions:
            raise ValidationError('Không có giao dịch nào để nhập')
        
        return transactions

    def save(self):
        """Lưu tất cả giao dịch vào database"""
        transactions = self.cleaned_data['transactions_data']
        created_count = 0
        
        for tx_data in transactions:
            # Tìm hoặc tạo danh mục
            category, _ = Category.objects.get_or_create(
                user=self.user,
                name=tx_data['category_name'],
                defaults={'type': tx_data['type']}
            )
            
            # Tạo giao dịch
            Transaction.objects.create(
                user=self.user,
                type=tx_data['type'],
                amount=tx_data['amount'],
                category=category,
                description=tx_data['description'],
                date=tx_data['date']
            )
            created_count += 1
        
        return created_count


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['month', 'year', 'amount', 'category']
        labels = {'month': 'Tháng', 'year': 'Năm', 'amount': 'Ngân sách (đ)', 'category': 'Danh mục'}
        widgets = {
            'month': forms.Select(choices=[(i, f'Tháng {i}') for i in range(1, 13)], attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020, 'max': 2030}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '10000', 'step': '10000'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            from django.db.models import Q
            # Hiển thị cả danh mục chi tiêu của user VÀ danh mục mặc định (khớp với trang /categories/)
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user, type='expense') | Q(is_default=True, type='expense')
            ).order_by('name')
        self.fields['category'].required = False
        self.fields['category'].empty_label = '-- Tất cả chi tiêu --'


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'deadline', 'icon']
        labels = {
            'name': 'Tên mục tiêu',
            'target_amount': 'Số tiền mục tiêu (đ)',
            'deadline': 'Hạn chót',
            'icon': 'Icon',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mua nhà, du lịch, ...'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1000', 'step': '1000'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '🎯, 🏠, ✈️, ...', 'maxlength': '50'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm min date cho deadline (ngày mai)
        from datetime import date, timedelta
        tomorrow = date.today() + timedelta(days=1)
        self.fields['deadline'].widget.attrs['min'] = tomorrow.strftime('%Y-%m-%d')
        
        # Nếu đã nạp tiền (current_amount > 0), khóa trường "Tên mục tiêu"
        if self.instance and self.instance.pk and int(self.instance.current_amount) > 0:
            self.fields['name'].disabled = True
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['class'] += ' bg-light'
            self.fields['name'].help_text = '⚠️ Không thể đổi tên sau khi đã nạp tiền (để đảm bảo hoàn tiền khi xóa)'
    
    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline:
            from datetime import date
            today = date.today()
            if deadline <= today:
                raise ValidationError('Hạn chót phải là ngày trong tương lai (sau ngày hôm nay).')
        return deadline
    
    def clean_target_amount(self):
        target_amount = self.cleaned_data.get('target_amount')
        # Nếu đã nạp tiền, số tiền mục tiêu phải >= số tiền đã nạp
        if self.instance and self.instance.pk and int(self.instance.current_amount) > 0:
            if target_amount < self.instance.current_amount:
                raise ValidationError(f'Số tiền mục tiêu phải lớn hơn hoặc bằng số tiền đã nạp ({int(self.instance.current_amount):,}đ).')
        return target_amount
    
    def save(self, commit=True):
        goal = super().save(commit=False)
        # Set icon mặc định nếu không có
        if not goal.icon:
            goal.icon = '🎯'
        if commit:
            goal.save()
        return goal


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        label='Ảnh đại diện',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    currency = forms.ChoiceField(
        required=False,
        label='Đơn vị tiền tệ',
        choices=[
            ('VND', 'VND'),
            ('USD', 'USD'),
            ('EUR', 'EUR'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {'first_name': 'Họ', 'last_name': 'Tên', 'email': 'Email'}
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load currency từ UserProfile
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['currency'].initial = self.instance.profile.currency
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        
        # Kiểm tra email đã tồn tại cho người dùng khác (loại trừ người dùng hiện tại)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Email này đã được sử dụng bởi người dùng khác. Vui lòng dùng email khác.')
        
        return email
    
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Kiểm tra kích thước file (tối đa 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('Kích thước ảnh không được vượt quá 5MB.')
            
            # Kiểm tra định dạng file
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = avatar.name.lower().split('.')[-1]
            if f'.{ext}' not in valid_extensions:
                raise ValidationError('Chỉ chấp nhận file ảnh: JPG, PNG, GIF, WEBP.')
        
        return avatar
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        
        # Lưu avatar và currency vào UserProfile
        if commit and hasattr(user, 'profile'):
            avatar_file = self.cleaned_data.get('avatar')
            currency = self.cleaned_data.get('currency')
            
            # Cập nhật currency
            if currency:
                user.profile.currency = currency
            
            # Lưu avatar
            if avatar_file:
                # Xóa ảnh cũ nếu có
                if user.profile.avatar_url:
                    import os
                    from django.conf import settings
                    old_path = os.path.join(settings.MEDIA_ROOT, user.profile.avatar_url)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Lưu ảnh mới
                from django.core.files.storage import default_storage
                filename = f'avatars/{user.id}_{avatar_file.name}'
                path = default_storage.save(filename, avatar_file)
                user.profile.avatar_url = path
            
            user.profile.save()
        
        return user


class ProfilePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Mật khẩu hiện tại',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label='Mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label='Xác nhận mật khẩu mới',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('Mật khẩu hiện tại không đúng')
        return current_password

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự')
        return new_password1

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError('Hai mật khẩu không khớp')
        return new_password2

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user
