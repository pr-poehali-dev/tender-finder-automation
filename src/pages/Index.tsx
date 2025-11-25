import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';
import Header from '@/components/Header';
import UserProfile from '@/components/UserProfile';
import CodeOutput from '@/components/CodeOutput';

const Index = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedCode, setGeneratedCode] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Ошибка',
        description: 'Введите описание задачи',
        variant: 'destructive',
      });
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('https://functions.poehali.dev/5baace72-d29f-474b-9400-53f1b555f8bb', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Ошибка генерации');
      }

      setGeneratedCode(data.code);
      toast({
        title: 'Успешно',
        description: 'Код сгенерирован',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error instanceof Error ? error.message : 'Не удалось сгенерировать код',
        variant: 'destructive',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card className="p-6">
              <div className="space-y-4">
                <div>
                  <h2 className="text-2xl font-bold mb-2">ИИ Генератор Кода</h2>
                  <p className="text-muted-foreground">
                    Опишите задачу, и ИИ создаст готовый код
                  </p>
                </div>

                <Textarea
                  placeholder="Например: Создай функцию для сортировки массива объектов по дате..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="min-h-[150px] resize-none"
                />

                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <Icon name="Loader2" className="mr-2 h-5 w-5 animate-spin" />
                      Генерация...
                    </>
                  ) : (
                    <>
                      <Icon name="Sparkles" className="mr-2 h-5 w-5" />
                      Сгенерировать код
                    </>
                  )}
                </Button>
              </div>
            </Card>

            {generatedCode && (
              <CodeOutput code={generatedCode} />
            )}
          </div>

          <div className="lg:col-span-1">
            <UserProfile />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;