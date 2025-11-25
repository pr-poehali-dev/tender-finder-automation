import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

interface CodeOutputProps {
  code: string;
}

const CodeOutput = ({ code }: CodeOutputProps) => {
  const { toast } = useToast();

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    toast({
      title: 'Скопировано',
      description: 'Код скопирован в буфер обмена',
    });
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Результат</h3>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleCopy}>
              <Icon name="Copy" className="mr-2 h-4 w-4" />
              Копировать
            </Button>
            <Button variant="outline" size="sm">
              <Icon name="Download" className="mr-2 h-4 w-4" />
              Скачать
            </Button>
          </div>
        </div>

        <Tabs defaultValue="code" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="code">Код</TabsTrigger>
            <TabsTrigger value="preview">Предпросмотр</TabsTrigger>
          </TabsList>
          
          <TabsContent value="code" className="mt-4">
            <div className="relative">
              <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                <code className="text-sm">{code}</code>
              </pre>
            </div>
          </TabsContent>
          
          <TabsContent value="preview" className="mt-4">
            <div className="bg-muted p-4 rounded-lg min-h-[200px] flex items-center justify-center">
              <p className="text-muted-foreground text-sm">
                Предпросмотр доступен для HTML/CSS/JS кода
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </Card>
  );
};

export default CodeOutput;
