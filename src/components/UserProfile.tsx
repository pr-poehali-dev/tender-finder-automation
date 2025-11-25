import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

const UserProfile = () => {
  const freeRequestsUsed = 3;
  const freeRequestsLimit = 5;
  const progressPercentage = (freeRequestsUsed / freeRequestsLimit) * 100;

  return (
    <Card className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
          <Icon name="User" className="h-6 w-6 text-primary" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">Гость</h3>
          <Badge variant="secondary" className="text-xs">Free Plan</Badge>
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
        <Button className="w-full" size="sm">
          <Icon name="Zap" className="mr-2 h-4 w-4" />
          Перейти на Pro
        </Button>
        <Button variant="outline" className="w-full" size="sm">
          <Icon name="LogIn" className="mr-2 h-4 w-4" />
          Войти
        </Button>
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
  );
};

export default UserProfile;
