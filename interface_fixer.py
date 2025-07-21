#!/usr/bin/env python3
"""
Interface Fixer - يضيف الواجهات المفقودة بذكاء
"""

def add_missing_interfaces():
    # قراءة infrastructure_services.py
    with open('src/application/interfaces/infrastructure_services.py', 'r') as f:
        content = f.read()
    
    # التحقق من عدم وجود الواجهات
    interfaces_to_add = []
    
    if 'class IExternalAPIClient' not in content:
        interfaces_to_add.append('''
class IExternalAPIClient(ABC):
    """Interface for external API integrations."""
    
    @abstractmethod
    async def make_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make request to external API endpoint."""
        pass
    
    @abstractmethod
    async def generate_response(
        self, child_id: str, conversation_history: list[str], current_input: str
    ) -> dict[str, Any]:
        """Generate AI response for child interaction."""
        pass
''')
    
    if 'class IConsentManager' not in content:
        interfaces_to_add.append('''
class IConsentManager(ABC):
    """Interface for COPPA consent management."""
    
    @abstractmethod
    async def verify_consent(self, child_id: str, operation: str) -> bool:
        """Verify parental consent for operation."""
        pass
''')
    
    if interfaces_to_add:
        # إضافة الواجهات
        with open('src/application/interfaces/infrastructure_services.py', 'a') as f:
            f.write('\n\n')
            f.write('\n'.join(interfaces_to_add))
        print("✅ تم إضافة الواجهات المفقودة")
    
    # تحديث read_model_interfaces.py
    with open('src/application/interfaces/read_model_interfaces.py', 'r') as f:
        content = f.read()
    
    if 'from .infrastructure_services import' not in content:
        # إضافة import بعد docstring
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '"""' and i > 0:  # نهاية docstring
                lines.insert(i + 1, '\nfrom .infrastructure_services import IEventBus, IExternalAPIClient, IConsentManager\n')
                break
        
        with open('src/application/interfaces/read_model_interfaces.py', 'w') as f:
            f.write('\n'.join(lines))
        print("✅ تم تحديث imports في read_model_interfaces.py")

if __name__ == "__main__":
    add_missing_interfaces()
