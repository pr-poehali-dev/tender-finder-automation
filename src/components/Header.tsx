import Icon from '@/components/ui/icon';

const Header = () => {
  return (
    <header className="border-b bg-card sticky top-0 z-50 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon name="Sparkles" className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold">CodeGen AI</h1>
              <p className="text-xs text-muted-foreground">ИИ Генератор Кода</p>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="#generator" className="text-sm font-medium hover:text-primary transition-colors">
              Генератор
            </a>
            <a href="https://t.me/YourBot" target="_blank" rel="noopener noreferrer" className="text-sm font-medium hover:text-primary transition-colors flex items-center gap-1">
              <Icon name="MessageCircle" className="h-4 w-4" />
              Telegram Бот
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;