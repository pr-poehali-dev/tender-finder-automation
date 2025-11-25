import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { useToast } from '@/hooks/use-toast';

interface User {
  id: number;
  username: string;
  email?: string;
  telegram_id?: number;
  is_premium: boolean;
  free_requests_used: number;
  free_requests_limit: number;
}

const UserProfile = () => {
  const [user, setUser] = useState<User | null>(null);
  const [showAuthDialog, setShowAuthDialog] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const savedUserId = localStorage.getItem('user_id');
    if (savedUserId) {
      fetchUser(savedUserId);
    }

    const handleUserUpdate = () => {
      const userId = localStorage.getItem('user_id');
      if (userId) {
        fetchUser(userId);
      }
    };

    window.addEventListener('user-updated', handleUserUpdate);
    return () => window.removeEventListener('user-updated', handleUserUpdate);
  }, []);

  const fetchUser = async (userId: string) => {
    try {
      const response = await fetch(`https://functions.poehali.dev/7659d4a3-2394-411f-857c-da1822fa43e0?user_id=${userId}`);
      const data = await response.json();
      if (response.ok && data.user) {
        setUser(data.user);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const handleAuth = async () => {
    if (!email || !username) {
      toast({
        title: 'Ошибка',
        description: 'Заполните все поля',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('https://functions.poehali.dev/7659d4a3-2394-411f-857c-da1822fa43e0', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username }),
      });

      const data = await response.json();
      if (response.ok && data.user) {
        setUser(data.user);
        localStorage.setItem('user_id', data.user.id.toString());
        setShowAuthDialog(false);
        toast({
          title: 'Успешно',
          description: 'Вы вошли в систему',
        });
      }
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось войти',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpgrade = async () => {
    if (!user) {
      toast({
        title: 'Ошибка',
        description: 'Сначала войдите в систему',
        variant: 'destructive',
      });
      return;
    }

    try {
      const response = await fetch('https://functions.poehali.dev/4a149312-f33f-4b05-b0ea-174164c38ad9', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, action: 'create_session' }),
      });

      const data = await response.json();
      if (response.ok && data.payment_url) {
        window.open(data.payment_url, '_blank');
      }
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось создать платеж',
        variant: 'destructive',
      });
    }
  };

  const freeRequestsUsed = user?.free_requests_used || 0;
  const freeRequestsLimit = user?.free_requests_limit || 5;
  const progressPercentage = (freeRequestsUsed / freeRequestsLimit) * 100;

  return (
    <>
      <Card className="p-6 space-y-6">
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Icon name="User" className="h-6 w-6 text-primary" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold">{user?.username || 'Гость'}</h3>
            <Badge variant={user?.is_premium ? 'default' : 'secondary'} className="text-xs">
              {user?.is_premium ? 'Pro' : 'Free'}
            </Badge>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Лимит запросов</span>
            <span className="font-medium">{freeRequestsUsed} / {freeRequestsLimit}</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
          <p className="text-xs text-muted-foreground">
            Осталось {freeRequestsLimit - freeRequestsUsed} бесплатных генераций
          </p>
        </div>

        <div className="space-y-2">
          {!user?.is_premium && (
            <Button onClick={handleUpgrade} className="w-full" size="sm">
              <Icon name="Zap" className="mr-2 h-4 w-4" />
              Перейти на Pro
            </Button>
          )}
          {!user && (
            <Button onClick={() => setShowAuthDialog(true)} variant="outline" className="w-full" size="sm">
              <Icon name="LogIn" className="mr-2 h-4 w-4" />
              Войти
            </Button>
          )}
        </div>

        <div className="pt-4 border-t space-y-3">
          <h4 className="text-sm font-semibold">Pro возможности</h4>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <Icon name="Check" className="h-4 w-4 text-primary" />
              Безлимитные генерации
            </li>
            <li className="flex items-center gap-2">
              <Icon name="Check" className="h-4 w-4 text-primary" />
              Приоритетная поддержка
            </li>
            <li className="flex items-center gap-2">
              <Icon name="Check" className="h-4 w-4 text-primary" />
              Расширенные модели ИИ
            </li>
          </ul>
        </div>
      </Card>

      <Dialog open={showAuthDialog} onOpenChange={setShowAuthDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Вход в систему</DialogTitle>
            <DialogDescription>
              Введите ваши данные для входа или регистрации
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 pt-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Имя</label>
              <Input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Ваше имя"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
              />
            </div>
            <Button onClick={handleAuth} disabled={isLoading} className="w-full">
              {isLoading ? (
                <>
                  <Icon name="Loader2" className="mr-2 h-4 w-4 animate-spin" />
                  Вход...
                </>
              ) : (
                'Войти'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default UserProfile;