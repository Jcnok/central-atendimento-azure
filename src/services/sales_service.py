from typing import Dict, List, Optional

class SalesService:
    # Mock Plans
    PLANS = {
        "basic": {"name": "Fibra 300 Mega", "price": 99.90, "features": ["WiFi 5", "Sem fidelidade"]},
        "standard": {"name": "Fibra 600 Mega", "price": 129.90, "features": ["WiFi 6", "Paramount+"]},
        "premium": {"name": "Fibra 1 Giga", "price": 199.90, "features": ["WiFi 6 Mesh", "HBO Max", "Paramount+"]}
    }

    @staticmethod
    def get_customer_profile(cliente_id: int) -> Dict[str, any]:
        """
        Retorna perfil do cliente (Mock).
        """
        # Simulação baseada no ID
        current_plan = "basic"
        if cliente_id % 2 == 0:
            current_plan = "standard"
            
        return {
            "cliente_id": cliente_id,
            "current_plan": SalesService.PLANS[current_plan],
            "usage_stats": {
                "avg_monthly_usage_gb": 450 if current_plan == "basic" else 800,
                "devices_connected": 5 if current_plan == "basic" else 12,
                "contract_age_months": 14
            }
        }

    @staticmethod
    def get_plan_recommendations(cliente_id: int) -> List[Dict[str, any]]:
        """
        Recomenda planos baseados no uso (Mock).
        """
        profile = SalesService.get_customer_profile(cliente_id)
        usage = profile["usage_stats"]
        current_plan_key = "basic" 
        for key, plan in SalesService.PLANS.items():
            if plan["name"] == profile["current_plan"]["name"]:
                current_plan_key = key
                break
        
        recommendations = []
        
        # Lógica simples de recomendação
        if usage["devices_connected"] > 8 and current_plan_key != "premium":
            recommendations.append({
                "plan": SalesService.PLANS["premium"],
                "reason": "Você tem muitos dispositivos conectados. O plano de 1 Giga com WiFi Mesh garantirá estabilidade para todos."
            })
        elif usage["avg_monthly_usage_gb"] > 400 and current_plan_key == "basic":
             recommendations.append({
                "plan": SalesService.PLANS["standard"],
                "reason": "Seu consumo de dados é alto. O plano de 600 Mega oferece melhor custo-benefício."
            })
            
        return recommendations

    @staticmethod
    def calculate_upgrade_cost(current_plan_name: str, new_plan_name: str) -> str:
        """
        Calcula diferença de preço.
        """
        def get_price(name):
            for p in SalesService.PLANS.values():
                if p["name"].lower() == name.lower():
                    return p["price"]
            return 0.0

        current_price = get_price(current_plan_name)
        new_price = get_price(new_plan_name)
        
        if new_price == 0:
            return "Plano não encontrado."
            
        diff = new_price - current_price
        
        if diff > 0:
            return f"O upgrade custará R$ {diff:.2f} a mais por mês."
        elif diff < 0:
            return f"Você economizará R$ {abs(diff):.2f} por mês."
        else:
            return "Os planos têm o mesmo preço."
