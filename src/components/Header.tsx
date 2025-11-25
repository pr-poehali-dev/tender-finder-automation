import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';

const Header = () => {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon name="Code2" className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">CodeGen AI</h1>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Главная
            </a>
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Документация
            </a>
            <a href="#" className="text-sm font-medium hover:text-primary transition-colors">
              Тарифы
            </a>
          </nav>

          <Button variant="ghost" size="sm">
            <Icon name="Menu" className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;
